import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

# --- Button to get recommendations ---
if st.button("✨ Get Recommendations"):

    # Prepare seeds
    seed_tracks = [t["id"] for t in top_tracks[:2]]
    seed_artists = [a["id"] for a in top_artists[:2]]
    seed_genres = user_genres[:1]  # Just 1 genre

    # Remove empty seeds to avoid errors
    seeds = {}
    if seed_tracks: seeds["seed_tracks"] = seed_tracks
    if seed_artists: seeds["seed_artists"] = seed_artists
    if seed_genres: seeds["seed_genres"] = seed_genres

    if not seeds:
        st.warning("Not enough seeds to generate recommendations.")
    else:
        try:
            recs = sp.recommendations(limit=10, **seeds)["tracks"]
            st.subheader("Recommended for You")
            st.markdown("<div class='recommendations'>", unsafe_allow_html=True)
            for track in recs:
                st.markdown(f"- [{track['name']} - {track['artists'][0]['name']}]({track['external_urls']['spotify']})")
            st.markdown("</div>", unsafe_allow_html=True)
        except spotipy.exceptions.SpotifyException as e:
            st.error(f"Could not generate recommendations: {e}")























