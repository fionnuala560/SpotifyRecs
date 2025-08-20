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
st.title("🎵 SpotifyRecs")
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
        .track-card, .artist-card, .genre-card {
            background-color: #1DB954;
            color: white;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 12px;
            font-weight: bold;
            transition: transform 0.2s;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .track-card:hover, .artist-card:hover, .genre-card:hover {
            transform: scale(1.02);
            cursor: pointer;
        }
        .track-card img, .artist-card img {
            border-radius: 8px;
            width: 50px;
            height: 50px;
            object-fit: cover;
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
    album_img = track['album']['images'][0]['url'] if track['album']['images'] else ""
    st.markdown(
        f"<div class='track-card'><img src='{album_img}'><span>{track['name']} - {track['artists'][0]['name']}</span></div>",
        unsafe_allow_html=True
    )

# --- Display Top Artists ---
st.subheader("Your Top Artists 🎤")
for artist in top_artists:
    artist_img = artist['images'][0]['url'] if artist['images'] else ""
    st.markdown(
        f"<div class='artist-card'><img src='{artist_img}'><span>{artist['name']}</span></div>",
        unsafe_allow_html=True
    )

# --- Extract genres from top artists ---
user_genres = []
for artist in top_artists:
    user_genres.extend(artist.get("genres", []))
user_genres = list(set(user_genres))[:5]

st.subheader("Your Top Genres 🎧")
for g in user_genres:
    st.markdown(
        f"<div class='genre-card'>{g.title()}</div>",
        unsafe_allow_html=True
    )

# --- Recommended Tracks by Genre (unique artists only) ---
st.subheader("Recommended Tracks 🎧")

# Initialize session state for recommendations
if "recommended_tracks" not in st.session_state:
    st.session_state.recommended_tracks = []
if "recommendations_generated" not in st.session_state:
    st.session_state.recommendations_generated = False

def fetch_recommendations():
    recommended_tracks = []
    seen_artists = set()
    seen_albums = set()

    for genre in user_genres:
        with st.spinner(f"Fetching top tracks for genre: {genre}..."):
            try:
                results = sp.search(q=f"genre:{genre}", type="track", limit=20)
                tracks = results.get("tracks", {}).get("items", [])
                for t in tracks:
                    artist_name = t["artists"][0]["name"]
                    album_name = t["album"]["name"]
                    if artist_name not in seen_artists and album_name not in seen_albums:
                        recommended_tracks.append({
                            "name": t["name"],
                            "artist": artist_name,
                            "album": album_name,
                            "url": t["external_urls"]["spotify"],
                            "img": t["album"]["images"][0]["url"] if t["album"]["images"] else ""
                        })
                        seen_artists.add(artist_name)
                        seen_albums.add(album_name)
            except spotipy.exceptions.SpotifyException as e:
                st.warning(f"Could not fetch tracks for genre {genre}: {e}")

    st.session_state.recommended_tracks = recommended_tracks
    st.session_state.recommendations_generated = True

# Show the initial button if recommendations haven't been generated
if not st.session_state.recommendations_generated:
    if st.button("Generate Recommendations"):
        fetch_recommendations()

# Show the recommendations if they exist
if st.session_state.recommendations_generated and st.session_state.recommended_tracks:
    st.markdown("""
        <style>
            .track-card {
                background-color: #1DB954;
                color: white;
                padding: 10px 15px;
                margin: 5px 0;
                border-radius: 12px;
                font-weight: bold;
                transition: transform 0.2s;
            }
            .track-card:hover {
                transform: scale(1.02);
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='recommendations'>", unsafe_allow_html=True)
    for t in st.session_state.recommended_tracks[:10]:
        st.markdown(
            f"<div class='track-card'><img src='{t['img']}' style='width:50px;height:50px;vertical-align:middle;margin-right:10px;'><a href='{t['url']}' target='_blank' style='color:white; text-decoration:none;'>{t['name']} - {t['artist']}</a></div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Show refresh button to regenerate recommendations
    if st.button("Refresh Recommendations"):
        st.session_state.recommendations_generated = False
        st.session_state.recommended_tracks = []
        fetch_recommendations()
































