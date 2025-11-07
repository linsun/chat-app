import streamlit as st
import redis
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Initialize Redis connection
@st.cache_resource
def get_redis_client():
    """Get Redis client (cached per session)"""
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,  # Automatically decode responses to strings
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        # Test connection
        client.ping()
        return client
    except Exception as e:
        st.error(f"Failed to connect to Redis: {str(e)}")
        return None

def init_votes():
    """Initialize vote counts in Redis if they don't exist"""
    redis_client = get_redis_client()
    if redis_client is None:
        return
    
    try:
        # Initialize if keys don't exist
        if not redis_client.exists("votes:classic_music"):
            redis_client.set("votes:classic_music", 0)
        if not redis_client.exists("votes:rock_music"):
            redis_client.set("votes:rock_music", 0)
    except Exception as e:
        st.error(f"Error initializing votes: {str(e)}")

def load_votes():
    """Load votes from Redis"""
    redis_client = get_redis_client()
    if redis_client is None:
        # Return default values if Redis is unavailable
        return {"classic_music": 0, "rock_music": 0}
    
    try:
        classic_votes = int(redis_client.get("votes:classic_music") or 0)
        rock_votes = int(redis_client.get("votes:rock_music") or 0)
        return {
            "classic_music": classic_votes,
            "rock_music": rock_votes
        }
    except Exception as e:
        st.error(f"Error loading votes: {str(e)}")
        return {"classic_music": 0, "rock_music": 0}

def increment_vote(choice):
    """Increment vote count for a choice (atomic operation in Redis)"""
    redis_client = get_redis_client()
    if redis_client is None:
        return load_votes()
    
    try:
        # Redis INCR is atomic, perfect for vote counting
        redis_client.incr(f"votes:{choice}")
        new_count = int(redis_client.get(f"votes:{choice}") or 0)
        logger.info(f"Vote recorded: {choice} - New count: {new_count}")
        return load_votes()
    except Exception as e:
        logger.error(f"Error incrementing vote for {choice}: {str(e)}")
        st.error(f"Error incrementing vote: {str(e)}")
        return load_votes()

def decrement_vote(choice):
    """Decrement vote count for a choice (atomic operation in Redis)"""
    redis_client = get_redis_client()
    if redis_client is None:
        return load_votes()
    
    try:
        # Use DECR and ensure it doesn't go below 0
        current = int(redis_client.get(f"votes:{choice}") or 0)
        if current > 0:
            redis_client.decr(f"votes:{choice}")
            new_count = int(redis_client.get(f"votes:{choice}") or 0)
            logger.info(f"Vote removed: {choice} - New count: {new_count}")
        return load_votes()
    except Exception as e:
        logger.error(f"Error decrementing vote for {choice}: {str(e)}")
        st.error(f"Error decrementing vote: {str(e)}")
        return load_votes()

def reset_all_votes():
    """Reset all votes to zero"""
    redis_client = get_redis_client()
    if redis_client is None:
        return
    
    try:
        redis_client.set("votes:classic_music", 0)
        redis_client.set("votes:rock_music", 0)
        logger.info("All votes reset to zero")
    except Exception as e:
        logger.error(f"Error resetting votes: {str(e)}")
        st.error(f"Error resetting votes: {str(e)}")

def check_and_reset_on_startup():
    """Reset votes if app just started (check Redis flag)"""
    redis_client = get_redis_client()
    if redis_client is None:
        return
    
    try:
        if not redis_client.exists("app:started"):
            # App just started, reset votes
            reset_all_votes()
            # Set flag to indicate app has started
            redis_client.set("app:started", "1")
    except Exception as e:
        st.error(f"Error checking startup flag: {str(e)}")

# Initialize votes
init_votes()

# Reset votes on app startup if needed
check_and_reset_on_startup()

# Initialize user's vote status (per session)
if "user_voted" not in st.session_state:
    st.session_state.user_voted = False

if "user_choice" not in st.session_state:
    st.session_state.user_choice = None

# Initialize music playback state
if "music_playing" not in st.session_state:
    st.session_state.music_playing = False

if "music_winner" not in st.session_state:
    st.session_state.music_winner = None

# Load current votes from Redis
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

# Reload votes to get latest from Redis (in case other clients voted)
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
        winner = "classic_music"
        st.success(f"🏆 **Classic Music is winning!** ({votes['classic_music']} vs {votes['rock_music']})")
    elif votes["rock_music"] > votes["classic_music"]:
        winner = "rock_music"
        st.success(f"🏆 **Rock Music is winning!** ({votes['rock_music']} vs {votes['classic_music']})")
    else:
        winner = None
        st.info("🤝 **It's a tie!** Both genres have the same number of votes.")
    
    st.markdown(f"**Total Votes:** {total_votes}")
    
    # Music playback section
    st.markdown("---")
    st.markdown("### 🎵 Play Winning Music")
    
    # Determine music track based on winner
    if winner == "classic_music":
        music_track = "roa-music-moonlight.mp3"
    elif winner == "rock_music":
        music_track = "Dust_in_the_wind.mp3"
    else:
        music_track = None
    
    # Music control button
    if st.button("▶️ Play Music", disabled=winner is None or music_track is None, use_container_width=True):
        st.session_state.music_playing = True
        st.session_state.music_winner = winner
        st.rerun()
    
    # Display audio player if music is playing
    if st.session_state.music_playing and st.session_state.music_winner == winner and music_track:
        audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), music_track)
        
        if os.path.exists(audio_path):
            st.audio(audio_path, autoplay=True)
            st.info(f"🎵 Now playing: {music_track}")
        else:
            st.error(f"Audio file not found: {audio_path}")
            st.session_state.music_playing = False
else:
    st.info("👆 Cast your vote above to see the results!")

# Auto-refresh every 2 seconds for live updates
time.sleep(2)
st.rerun()
