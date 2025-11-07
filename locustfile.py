"""
Locust stress test for the vote app.
Install: pip install locust
Run: locust -f locustfile.py --host=http://localhost:8501
Then open http://localhost:8089 in browser

This uses the test API endpoint to directly increment votes.
"""

from locust import HttpUser, task, between
import random
import json

CHOICES = ["classic_music", "rock_music"]

class VoteUser(HttpUser):
    """Simulates a user voting on the app"""
    wait_time = between(0.5, 2)  # Wait 0.5-2 seconds between votes
    
    @task(10)
    def vote_classic(self):
        """Vote for classic music via test API"""
        with self.client.get(
            "/3_Test_API",
            params={"vote": "classic_music"},
            name="Vote Classic",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    # Check if response contains success
                    if "success" in response.text.lower() or "count" in response.text.lower():
                        response.success()
                    else:
                        response.failure("Vote not recorded")
                except:
                    response.success()  # Assume success if we can't parse
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(10)
    def vote_rock(self):
        """Vote for rock music via test API"""
        with self.client.get(
            "/3_Test_API",
            params={"vote": "rock_music"},
            name="Vote Rock",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    if "success" in response.text.lower() or "count" in response.text.lower():
                        response.success()
                    else:
                        response.failure("Vote not recorded")
                except:
                    response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(1)
    def view_vote_page(self):
        """View the vote page to see results"""
        self.client.get("/2_Vote", name="View Vote Page")
    
    def on_start(self):
        """Called when a user starts"""
        # Access the app first
        self.client.get("/", name="Home")

