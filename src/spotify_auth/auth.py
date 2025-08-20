import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

def authenticate_spotify():
    # Initialize the authenticated flag if it doesn't exist
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Clear cache and session state if there's an error
    if "token_info" in st.session_state and st.session_state["token_info"] is None:
        del st.session_state["token_info"]
        st.session_state.authenticated = False

    sp_oauth = SpotifyOAuth(
        client_id=st.secrets["spotify"]["client_id"],
        client_secret=st.secrets["spotify"]["client_secret"],
        redirect_uri=st.secrets["spotify"]["redirect_uri"],
        scope="user-library-read user-read-recently-played user-top-read",
        cache_path=None,
        show_dialog=True
    )

    # If we don't have token info, check for code in query params or show login button
    if "token_info" not in st.session_state:
        if "code" in st.query_params:
            code = st.query_params["code"]
            try:
                token_info = sp_oauth.get_access_token(code, as_dict=True)
                st.session_state["token_info"] = token_info
                st.session_state.authenticated = True
            except spotipy.oauth2.SpotifyOauthError:
                st.warning("Please authenticate with Spotify")
                st.session_state.authenticated = False
                return None
        elif not st.session_state.authenticated:
            auth_url = sp_oauth.get_authorize_url()
            # Styled Spotify login button
            st.markdown(
                f"""
                <a href="{auth_url}" target="_self">
                    <button style="
                        background-color: #1DB954;
                        color: white;
                        padding: 0.75rem 1.5rem;
                        border: none;
                        border-radius: 12px;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                        margin-top: 1rem;
                    ">
                        Log in with Spotify
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )

    # Check if token exists and refresh if needed
    token_info = st.session_state.get("token_info")
    if token_info and sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            st.session_state["token_info"] = token_info
        except Exception:
            del st.session_state["token_info"]
            st.session_state.authenticated = False
            return None

    # Return authenticated Spotify client if ready
    if token_info:
        st.session_state.authenticated = True
        return spotipy.Spotify(auth=token_info["access_token"])

    return None

# Usage
sp = authenticate_spotify()
if sp:
    st.success("Logged in with Spotify!")

