import streamlit as st
from auth.tinder_login import TinderLogin
from auth.session_manager import SessionManager
from ai_matcher.matching import MatchGenerator
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Initialize services
session_manager = SessionManager()
matcher = MatchGenerator()

# Configure Streamlit
st.set_page_config(
    page_title="Tinder AI Matcher",
    page_icon="💘",
    layout="wide"
)

def display_profile(profile):
    """Display a profile card with interactive elements"""
    with st.container():
        cols = st.columns([1, 3])
        
        with cols[0]:
            if profile.get("images"):
                st.image(profile["images"][0], width=200)
            
            if profile.get("score"):
                st.metric("Match Score", f"{profile['score']}%")
            
            if profile.get("distance_km"):
                st.caption(f"{round(profile['distance_km'], 1)} km away")
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❤️ Like", key=f"like_{profile['id']}"):
                    if matcher.api.like_profile(profile["id"]):
                        st.success("Liked!")
            with col2:
                if st.button("✖️ Pass", key=f"pass_{profile['id']}"):
                    if matcher.api.pass_profile(profile["id"]):
                        st.info("Passed")
        
        with cols[1]:
            st.subheader(f"{profile.get('name')}, {profile.get('age')}")
            
            # Basic info
            if profile.get("bio"):
                st.write(profile["bio"])
            
            # Details section
            with st.expander("Details"):
                if profile.get("schools"):
                    st.write("**Education:** " + ", ".join(profile["schools"]))
                
                if profile.get("jobs"):
                    st.write("**Work:** " + ", ".join(profile["jobs"]))
                
                if profile.get("interests"):
                    st.write("**Interests:** " + ", ".join(profile["interests"]))
            
            # AI analysis
            if profile.get("analysis"):
                with st.expander("AI Analysis"):
                    st.write(profile["analysis"])

def authenticate():
    """Handle authentication flow"""
    st.title("Tinder AI Matcher Login")
    
    if st.button("Login with Google"):
        with st.spinner("Logging in to Tinder..."):
            # Start automated login
            login = TinderLogin(headless=False)
            auth_token = login.get_auth_token()
            
            if auth_token:
                session_manager.save_session(auth_token)
                st.session_state.auth_token = auth_token
                st.success("Login successful!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Login failed. Please try again.")

def main_app():
    """Main application after authentication"""
    st.title("💘 Tinder AI Matcher")
    st.write("Powered by GPT-4 and real-time matching")
    
    # Sidebar for preferences
    with st.sidebar:
        st.header("Matching Preferences")
        
        gender_pref = st.selectbox("Interested in", ["Men", "Women", "Everyone"])
        age_range = st.slider("Age Range", 18, 100, (22, 30))
        max_distance = st.slider("Max Distance (km)", 1, 100, 50)
        
        if st.button("Find Matches"):
            with st.spinner("Finding your best matches..."):
                # Get user profile from Tinder
                user_profile = matcher.api.get_self_profile()
                
                if not user_profile:
                    st.error("Failed to fetch your profile")
                    return
                
                # Generate matches
                preferences = {
                    "gender": gender_pref,
                    "min_age": age_range[0],
                    "max_age": age_range[1],
                    "max_distance": max_distance
                }
                
                st.session_state.matches = matcher.generate_matches(
                    user_profile, 
                    preferences
                )
    
    # Display matches
    if "matches" in st.session_state and st.session_state.matches:
        st.header("Your AI-Selected Matches")
        
        for profile in st.session_state.matches[:10]:  # Show top 10
            display_profile(profile)
    else:
        st.info("Set your preferences and click 'Find Matches'")

def main():
    """Main entry point"""
    # Check for existing session
    if "auth_token" not in st.session_state:
        auth_token = session_manager.load_session()
        if auth_token:
            st.session_state.auth_token = auth_token
            matcher.api.auth_token = auth_token
    
    # Show appropriate view based on auth state
    if "auth_token" in st.session_state and st.session_state.auth_token:
        main_app()
    else:
        authenticate()

if __name__ == "__main__":
    main()
