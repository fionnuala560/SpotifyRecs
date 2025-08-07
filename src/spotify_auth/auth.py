import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st


def authenticate_spotify():
    # Clear cache and session state if there's an error
    if "token_info" in st.session_state and st.session_state["token_info"] is None:
        del st.session_state["token_info"]

    sp_oauth = SpotifyOAuth(
        client_id=st.secrets["spotify"]["client_id"],
        client_secret=st.secrets["spotify"]["client_secret"],
        redirect_uri=st.secrets["spotify"]["redirect_uri"],
        scope="user-library-read user-read-recently-played user-top-read",
        cache_path=None,  # Disable file caching
        show_dialog=True  # Force re-authentication
    )

    if "token_info" not in st.session_state:
        # Only show login message if there's no code in query params
        if "code" not in st.query_params:
            auth_url = sp_oauth.get_authorize_url()
            st.markdown(f"[Click here to log in with Spotify]({auth_url})")
        else:
            code = st.query_params["code"]
            try:
                token_info = sp_oauth.get_access_token(code, as_dict=True)
                st.session_state["token_info"] = token_info
            except spotipy.oauth2.SpotifyOauthError as e:
                st.warning(f"Please authenticate with Spotify")
                return None

    # Get token info from session state
    token_info = st.session_state.get("token_info")

    # Refresh token if expired
    if token_info and sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            st.session_state["token_info"] = token_info
        except Exception:
            del st.session_state["token_info"]
            return None

    if token_info:
        return spotipy.Spotify(auth=token_info["access_token"])

    return None
