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

    if "token_info" not in st.session_state:
        if "code" in st.query_params:
            code = st.query_params["code"]
            try:
                token_info = sp_oauth.get_access_token(code, as_dict=True)
                st.session_state["token_info"] = token_info
                st.session_state.authenticated = True
            except spotipy.oauth2.SpotifyOauthError as e:
                st.warning("Please authenticate with Spotify")
                st.session_state.authenticated = False
                return None
        elif not st.session_state.authenticated:
            auth_url = sp_oauth.get_authorize_url()
            st.markdown(f"[Click here to log in with Spotify]({auth_url})")

    token_info = st.session_state.get("token_info")

    if token_info and sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            st.session_state["token_info"] = token_info
        except Exception:
            del st.session_state["token_info"]
            st.session_state.authenticated = False
            return None

    if token_info:
        st.session_state.authenticated = True
        return spotipy.Spotify(auth=token_info["access_token"])

    return None
