import streamlit as st
import sqlite3
import os
import time
from contextlib import contextmanager

# Database file to store votes (shared across all clients)
VOTES_DB = os.getenv("VOTES_DB", "votes.db")
# Flag file to track if votes have been reset on app startup
APP_STARTED_FLAG = os.getenv("APP_STARTED_FLAG", "app_started.flag")

@contextmanager
def get_db_connection():
    """Get database connection with proper error handling"""
    conn = sqlite3.connect(VOTES_DB, timeout=10.0)  # 10 second timeout for concurrent access
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize the database with votes table"""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                choice TEXT PRIMARY KEY,
                count INTEGER DEFAULT 0
            )
        """)
        # Initialize with default values if table is empty
        cursor = conn.execute("SELECT COUNT(*) FROM votes")
        if cursor.fetchone()[0] == 0:
            conn.execute("INSERT INTO votes (choice, count) VALUES ('classic_music', 0)")
            conn.execute("INSERT INTO votes (choice, count) VALUES ('rock_music', 0)")

def load_votes():
    """Load votes from database"""
    init_database()
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT choice, count FROM votes")
        votes = {row[0]: row[1] for row in cursor.fetchall()}
        # Ensure both choices exist
        if "classic_music" not in votes:
            votes["classic_music"] = 0
        if "rock_music" not in votes:
            votes["rock_music"] = 0
        return votes

def increment_vote(choice):
    """Increment vote count for a choice (thread-safe with SQLite)"""
    init_database()
    max_retries = 5
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            with get_db_connection() as conn:
                # Use SQLite's atomic increment
                conn.execute("""
                    INSERT INTO votes (choice, count) 
                    VALUES (?, 1)
                    ON CONFLICT(choice) DO UPDATE SET count = count + 1
                """, (choice,))
                conn.commit()
                return load_votes()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                # Database is locked, retry with exponential backoff
                time.sleep(retry_delay * (2 ** attempt))
                continue
            else:
                st.error(f"Database error: {str(e)}")
                return load_votes()
        except Exception as e:
            st.error(f"Error incrementing vote: {str(e)}")
            return load_votes()
    
    # If all retries failed, return current votes
    return load_votes()

def decrement_vote(choice):
    """Decrement vote count for a choice (thread-safe with SQLite)"""
    init_database()
    max_retries = 5
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            with get_db_connection() as conn:
                # Use SQLite's atomic decrement
                conn.execute("""
                    UPDATE votes 
                    SET count = MAX(0, count - 1)
                    WHERE choice = ? AND count > 0
                """, (choice,))
                conn.commit()
                return load_votes()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                # Database is locked, retry with exponential backoff
                time.sleep(retry_delay * (2 ** attempt))
                continue
            else:
                st.error(f"Database error: {str(e)}")
                return load_votes()
        except Exception as e:
            st.error(f"Error decrementing vote: {str(e)}")
            return load_votes()
    
    # If all retries failed, return current votes
    return load_votes()

def reset_all_votes():
    """Reset all votes to zero"""
    init_database()
    with get_db_connection() as conn:
        conn.execute("UPDATE votes SET count = 0")
        conn.commit()

def check_and_reset_on_startup():
    """Reset votes if app just started (flag file doesn't exist)"""
    if not os.path.exists(APP_STARTED_FLAG):
        # App just started, reset votes
        reset_all_votes()
        # Create flag file to indicate app has started
        try:
            with open(APP_STARTED_FLAG, 'w') as f:
                f.write("")
        except Exception:
            pass  # Ignore errors creating flag file

# Initialize database
init_database()

# Reset votes on app startup if needed
check_and_reset_on_startup()

# Initialize user's vote status (per session)
if "user_voted" not in st.session_state:
    st.session_state.user_voted = False

if "user_choice" not in st.session_state:
    st.session_state.user_choice = None

# Load current votes from database
votes = load_votes()

st.title("🎵 Music Preference Vote")

# Voting buttons
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎼 Classic Music")
    if st.button("Vote for Classic Music", key="classic", use_container_width=True, type="primary" if st.session_state.user_choice == "classic_music" else "secondary"):
        if not st.session_state.user_voted:
            # First vote from this user
            votes = increment_vote("classic_music")
            st.session_state.user_voted = True
            st.session_state.user_choice = "classic_music"
            st.success("✅ You voted for Classic Music!")
            st.rerun()
        else:
            # User already voted, allow changing vote
            if st.session_state.user_choice != "classic_music":
                # Remove previous vote
                votes = decrement_vote(st.session_state.user_choice)
                # Add new vote
                votes = increment_vote("classic_music")
                st.session_state.user_choice = "classic_music"
                st.success("✅ You changed your vote to Classic Music!")
                st.rerun()
            else:
                st.info("You already voted for Classic Music!")

with col2:
    st.markdown("### 🎸 Rock Music")
    if st.button("Vote for Rock Music", key="rock", use_container_width=True, type="primary" if st.session_state.user_choice == "rock_music" else "secondary"):
        if not st.session_state.user_voted:
            # First vote from this user
            votes = increment_vote("rock_music")
            st.session_state.user_voted = True
            st.session_state.user_choice = "rock_music"
            st.success("✅ You voted for Rock Music!")
            st.rerun()
        else:
            # User already voted, allow changing vote
            if st.session_state.user_choice != "rock_music":
                # Remove previous vote
                votes = decrement_vote(st.session_state.user_choice)
                # Add new vote
                votes = increment_vote("rock_music")
                st.session_state.user_choice = "rock_music"
                st.success("✅ You changed your vote to Rock Music!")
                st.rerun()
            else:
                st.info("You already voted for Rock Music!")

st.markdown("---")

# Reload votes to get latest from database (in case other clients voted)
votes = load_votes()

# Display results
st.markdown("### 📊 Live Vote Results")

total_votes = votes["classic_music"] + votes["rock_music"]

if total_votes > 0:
    classic_percentage = (votes["classic_music"] / total_votes) * 100
    rock_percentage = (votes["rock_music"] / total_votes) * 100
    
    # Display vote counts
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🎼 Classic Music", 
                 f"{votes['classic_music']} votes",
                 f"{classic_percentage:.1f}%")
    
    with col2:
        st.metric("🎸 Rock Music",
                 f"{votes['rock_music']} votes",
                 f"{rock_percentage:.1f}%")
    
    # Progress bars
    st.markdown("#### Vote Distribution")
    st.progress(classic_percentage / 100, text=f"Classic Music: {classic_percentage:.1f}%")
    st.progress(rock_percentage / 100, text=f"Rock Music: {rock_percentage:.1f}%")
    
    # Bar chart
    st.markdown("#### Visual Results")
    chart_data = {
        "Classic Music": votes["classic_music"],
        "Rock Music": votes["rock_music"]
    }
    st.bar_chart(chart_data)
    
    # Winner
    st.markdown("---")
    if votes["classic_music"] > votes["rock_music"]:
        st.success(f"🏆 **Classic Music is winning!** ({votes['classic_music']} vs {votes['rock_music']})")
    elif votes["rock_music"] > votes["classic_music"]:
        st.success(f"🏆 **Rock Music is winning!** ({votes['rock_music']} vs {votes['classic_music']})")
    else:
        st.info("🤝 **It's a tie!** Both genres have the same number of votes.")
    
    st.markdown(f"**Total Votes:** {total_votes}")
else:
    st.info("👆 Cast your vote above to see the results!")

# Auto-refresh every 2 seconds for live updates
time.sleep(2)
st.rerun()
