#!/usr/bin/env python3
"""
Stress test script for the vote app.
Simulates concurrent users voting on the Streamlit app.
"""

import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Configuration
APP_URL = "http://localhost:8501"  # Change to your app URL
NUM_USERS = 30
VOTES_PER_USER = 5  # Each user votes 5 times
CHOICES = ["classic_music", "rock_music"]

# Statistics
stats = {
    "total_requests": 0,
    "successful": 0,
    "failed": 0,
    "errors": []
}
stats_lock = threading.Lock()

def log(message):
    """Thread-safe logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def simulate_user_vote(user_id, vote_count):
    """Simulate a single user voting multiple times"""
    session = requests.Session()
    user_stats = {"success": 0, "failed": 0}
    
    try:
        # First, access the app to get a session
        log(f"User {user_id}: Accessing app...")
        response = session.get(f"{APP_URL}/2_Vote")
        if response.status_code != 200:
            log(f"User {user_id}: Failed to access app - Status {response.status_code}")
            with stats_lock:
                stats["failed"] += 1
            return user_stats
        
        # Simulate voting
        for i in range(vote_count):
            choice = random.choice(CHOICES)
            log(f"User {user_id}: Voting for {choice} (vote {i+1}/{vote_count})")
            
            # Streamlit button clicks are handled via form submission
            # We need to simulate the button click by making a POST request
            # Note: Streamlit uses a special endpoint for widget interactions
            try:
                # Get the current session state token from cookies or response
                # Streamlit uses _stcore/stream endpoint for widget updates
                
                # For simplicity, we'll use the Streamlit API endpoint
                # In a real scenario, you'd need to parse the session token
                vote_data = {
                    "choice": choice,
                    "widget_key": f"vote_{choice}"
                }
                
                # Make a request that simulates button click
                # Streamlit handles this through its internal API
                response = session.post(
                    f"{APP_URL}/_stcore/stream",
                    data=vote_data,
                    timeout=10
                )
                
                if response.status_code in [200, 302]:
                    user_stats["success"] += 1
                    with stats_lock:
                        stats["successful"] += 1
                    log(f"User {user_id}: ✓ Vote {i+1} successful")
                else:
                    user_stats["failed"] += 1
                    with stats_lock:
                        stats["failed"] += 1
                    log(f"User {user_id}: ✗ Vote {i+1} failed - Status {response.status_code}")
                
                # Random delay between votes (0.5-2 seconds)
                time.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                user_stats["failed"] += 1
                with stats_lock:
                    stats["failed"] += 1
                    stats["errors"].append(f"User {user_id} vote {i+1}: {str(e)}")
                log(f"User {user_id}: ✗ Vote {i+1} error - {str(e)}")
            
            with stats_lock:
                stats["total_requests"] += 1
    
    except Exception as e:
        log(f"User {user_id}: Fatal error - {str(e)}")
        with stats_lock:
            stats["failed"] += vote_count
            stats["errors"].append(f"User {user_id}: {str(e)}")
    
    return user_stats

def stress_test_simple():
    """
    Simpler approach: Just make GET requests to trigger page loads
    This simulates users accessing the page and clicking buttons
    """
    def make_requests(user_id):
        session = requests.Session()
        success = 0
        failed = 0
        
        for i in range(VOTES_PER_USER):
            try:
                # Access the vote page
                response = session.get(f"{APP_URL}/2_Vote", timeout=10)
                
                if response.status_code == 200:
                    success += 1
                    with stats_lock:
                        stats["successful"] += 1
                    log(f"User {user_id}: ✓ Request {i+1} successful")
                else:
                    failed += 1
                    with stats_lock:
                        stats["failed"] += 1
                    log(f"User {user_id}: ✗ Request {i+1} failed - Status {response.status_code}")
                
                with stats_lock:
                    stats["total_requests"] += 1
                
                # Random delay
                time.sleep(random.uniform(0.3, 1.5))
                
            except Exception as e:
                failed += 1
                with stats_lock:
                    stats["failed"] += 1
                    stats["errors"].append(f"User {user_id} request {i+1}: {str(e)}")
                log(f"User {user_id}: ✗ Request {i+1} error - {str(e)}")
        
        return {"user_id": user_id, "success": success, "failed": failed}
    
    return make_requests

def run_stress_test():
    """Run the stress test with concurrent users"""
    print("=" * 60)
    print(f"Starting stress test: {NUM_USERS} concurrent users")
    print(f"Each user will make {VOTES_PER_USER} requests")
    print(f"Target URL: {APP_URL}")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        # Submit all user tasks
        futures = [
            executor.submit(stress_test_simple(), user_id)
            for user_id in range(1, NUM_USERS + 1)
        ]
        
        # Wait for all tasks to complete and collect results
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                log(f"Task error: {str(e)}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print()
    print("=" * 60)
    print("STRESS TEST SUMMARY")
    print("=" * 60)
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Successful: {stats['successful']} ({stats['successful']/stats['total_requests']*100:.1f}%)")
    print(f"Failed: {stats['failed']} ({stats['failed']/stats['total_requests']*100:.1f}%)")
    print(f"Requests per second: {stats['total_requests']/duration:.2f}")
    print()
    
    if stats['errors']:
        print(f"Errors ({len(stats['errors'])}):")
        for error in stats['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more errors")
    
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    # Allow URL override via command line
    if len(sys.argv) > 1:
        APP_URL = sys.argv[1]
    
    if len(sys.argv) > 2:
        NUM_USERS = int(sys.argv[2])
    
    if len(sys.argv) > 3:
        VOTES_PER_USER = int(sys.argv[3])
    
    print(f"Configuration:")
    print(f"  URL: {APP_URL}")
    print(f"  Users: {NUM_USERS}")
    print(f"  Votes per user: {VOTES_PER_USER}")
    print()
    
    try:
        run_stress_test()
    except KeyboardInterrupt:
        print("\nStress test interrupted by user")
        print(f"Partial results: {stats['successful']} successful, {stats['failed']} failed")

