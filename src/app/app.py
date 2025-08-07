import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spotify_auth.auth import authenticate_spotify

# Initial session state
if "view" not in st.session_state:
    st.session_state.view = "stats"

# Authenticate with Spotify
sp = authenticate_spotify()
if not sp:
    st.stop()

# -- HEADER --
st.markdown(
    """
    <div padding: 2rem; border-radius: 10px;'>
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>🎵 SpotifyRecs</h1>
        <p style='color: white; font-size: 1.2rem;'>Your personal Spotify stats and music recommendations</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- USER STATS VIEW ----

top_tracks = sp.current_user_top_tracks(limit=10)
top_artists = sp.current_user_top_artists(limit=10)

genres = []
for artist in top_artists["items"]:
    genres.extend(artist["genres"])
top_genres = list(set(genres))[:10]

top_albums = list({
                      track['album']['id']: track['album']
                      for track in top_tracks["items"]
                  }.values())

sections = [
    {
        "title": "Top Tracks",
        "content": [
            f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}"
            for track in top_tracks["items"]
        ]
    },
    {
        "title": "Top Artists",
        "content": [artist['name'] for artist in top_artists["items"]]
    },
    {
        "title": "Top Genres",
        "content": top_genres
    },
    {
        "title": "Top Albums",
        "content": [
            f"{album['name']} by {', '.join(artist['name'] for artist in album['artists'])}"
            for album in top_albums
        ]
    }
]

for i in range(0, len(sections), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(sections):
            section = sections[i + j]
            with cols[j]:
                st.markdown(
                    f"""
                        <div style='
                            background-color: #1DB954;
                            padding: 1.5rem;
                            border-radius: 20px;
                            margin-bottom: 2rem;
                        '>
                            <h3 style='color:white; text-align:center;'>{section['title']}</h3>
                            <ul style='color:white; font-size: 0.9rem; padding-left: 1rem;'>
                                {''.join(f"<li>{item}</li>" for item in section['content'][:10])}
                            </ul>
                        </div>
                        """,
                    unsafe_allow_html=True
                )

st.markdown(
    """
    <style>
    .recommend-button button {
        background-color: #1DB954;
        color: white;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        border: none;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("🔁 Generate Recommendations", key="generate_recommendations_button"):
    st.session_state.view = "recommendations"
    st.experimental_rerun()


# # ---- RECOMMENDATIONS VIEW ----
# elif st.session_state.view == "recommendations":
#     st.markdown("## 🌟 Your Recommendations")
#
#     # Use top artist/track IDs for seed
#     seed_artists = [a["id"] for a in sp.current_user_top_artists(limit=1)["items"]]
#     seed_tracks = [t["id"] for t in sp.current_user_top_tracks(limit=1)["items"]]
#
#     recs = sp.recommendations(seed_artists=seed_artists, seed_tracks=seed_tracks, limit=10)
#
#     st.markdown("#### 🔊 Recommended Tracks")
#     for track in recs["tracks"]:
#         st.write(f"- {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
#
#     st.markdown("#### 🎤 Recommended Artists")
#     artist_names = set()
#     for track in recs["tracks"]:
#         for artist in track["artists"]:
#             artist_names.add(artist["name"])
#     for name in list(artist_names)[:10]:
#         st.write(f"- {name}")
#
#     st.markdown("#### 🧬 Estimated Genres")
#     genre_list = []
#     for artist in recs["tracks"][0]["artists"]:
#         artist_data = sp.artist(artist["id"])
#         genre_list.extend(artist_data.get("genres", []))
#     for genre in list(set(genre_list))[:10]:
#         st.write(f"- {genre}")
#
#     # Back button
#     if st.button("⬅️ Back to Your Stats"):
#         st.session_state.view = "stats"
#         st.experimental_rerun()