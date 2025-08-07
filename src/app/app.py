import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spotify_auth.auth import authenticate_spotify


st.markdown(
    """
    <div padding: 2rem; border-radius: 10px;'>
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>🎵 SpotifyRecs</h1>
        <p style='color: white; font-size: 1.2rem;'>Your personal Spotify stats and music recommendations</p>
    </div>
    """,
    unsafe_allow_html=True
)

sp = authenticate_spotify()
if not sp:
    st.stop()

if sp:
    user = sp.current_user()
    st.write(f"Welcome, {user['display_name']}!")

    results = sp.current_user_top_tracks(limit=10)
    for item in results['items']:
        st.write(f"{item['name']} by {', '.join(artist['name'] for artist in item['artists'])}")
else:
    st.write("Authentication failed. Please try again.")