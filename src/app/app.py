import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spotify_auth.auth import authenticate_spotify


st.title("Spotify Data Explorer")

sp = authenticate_spotify()

if sp:
    user = sp.current_user()
    st.write(f"Welcome, {user['display_name']}!")

    results = sp.current_user_recently_played(limit=10)
    for item in results['items']:
        track = item['track']
        st.write(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
else:
    st.write("Authentication failed. Please try again.")