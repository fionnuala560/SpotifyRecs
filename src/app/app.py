import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spotify_auth.auth import authenticate_spotify

# --- Spotify API Setup ---
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8888/callback",
    scope="user-top-read"
))

# --- Streamlit Page Config ---
st.set_page_config(page_title="Spotify Recs App", page_icon="🎵", layout="centered")

# --- Title and Header ---
st.title("🎵 My Spotify Recommendations App")
st.header("Discover tracks, artists, and genres tailored for you")
st.write("See your top Spotify tracks, artists, and genres, and get personalized recommendations.")

# Initial session state
if "view" not in st.session_state:
    st.session_state.view = "stats"

# Authenticate with Spotify
sp = authenticate_spotify()
if not sp:
    st.stop()

# --- Custom CSS ---
st.markdown("""
    <style>
        .box {
            background-color: #1DB954;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            color: black;
            font-weight: bold;
        }
        .recommendations {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            background-color: #191414;
            color: white;
        }
        .recommendations a {
            color: #1DB954;
            text-decoration: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- Fetch User's Top Data ---
with st.spinner("Fetching your top Spotify data..."):
    top_tracks = sp.current_user_top_tracks(limit=10, time_range="short_term")["items"]
    top_artists = sp.current_user_top_artists(limit=10, time_range="short_term")["items"]

# --- Display Top Tracks ---
st.subheader("Your Top Tracks 🎶")
for track in top_tracks:
    st.markdown(f"<div class='box'>{track['name']} - {track['artists'][0]['name']}</div>", unsafe_allow_html=True)

# --- Display Top Artists ---
st.subheader("Your Top Artists 🎤")
for artist in top_artists:
    st.markdown(f"<div class='box'>{artist['name']}</div>", unsafe_allow_html=True)

# --- Extract genres from top artists ---
user_genres = []
for artist in top_artists:
    user_genres.extend(artist.get("genres", []))
user_genres = list(set(user_genres))[:5]

st.subheader("Your Top Genres 🎧")
for g in user_genres:
    st.markdown(f"<div class='box'>{g.title()}</div>", unsafe_allow_html=True)


# --- Get Top Tracks by Genre ---
st.subheader("Recommended Tracks by Genre 🎧")

if user_genres:
    recommended_tracks = []

    for genre in user_genres:
        with st.spinner(f"Fetching top tracks for genre: {genre}..."):
            try:
                results = sp.search(q=f"genre:{genre}", type="track", limit=5)
                tracks = results.get("tracks", {}).get("items", [])
                for t in tracks:
                    recommended_tracks.append({
                        "name": t["name"],
                        "artist": t["artists"][0]["name"],
                        "url": t["external_urls"]["spotify"]
                    })
            except spotipy.exceptions.SpotifyException as e:
                st.warning(f"Could not fetch tracks for genre {genre}: {e}")

    if recommended_tracks:
        st.markdown("<div class='recommendations'>", unsafe_allow_html=True)
        for t in recommended_tracks:
            st.markdown(f"- [{t['name']} - {t['artist']}]({t['url']})")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Couldn't find top tracks for your genres.")
else:
    st.info("No genres found from your top artists.")



























