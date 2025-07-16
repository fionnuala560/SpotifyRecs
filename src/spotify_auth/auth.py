import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import os

client_id = st.secrets["spotify"]["client_id"]
client_secret = st.secrets["spotify"]["client_secret"]
redirect_uri = st.secrets["spotify"]["redirect_uri"]
scope = "user-library-read user-read-recently-played user-top-read"

def authenticate_spotify():
    if "token_info" not in st.session_state:
        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=".cache"
        )

        token_info = sp_oauth.get_cached_token()
        if not token_info:
            auth_url = sp_oauth.get_authorize_url()
            st.markdown(f"### Step 1: [Click here to log in with Spotify]({auth_url})")

            query_params = st.query_params
            if "code" in query_params:
                code = query_params["code"][0]
                try:
                    token_info = sp_oauth.get_access_token(code, as_dict=True)
                    st.session_state.token_info = token_info
                except spotipy.oauth2.SpotifyOauthError:
                    st.error("There was a problem authorizing with Spotify. Try logging in again.")
                    return None
        else:
            st.session_state.token_info = token_info

    token_info = st.session_state.get("token_info")
    if token_info and not SpotifyOAuth(client_id, client_secret, redirect_uri).is_token_expired(token_info):
        sp = spotipy.Spotify(auth=token_info["access_token"])
        return sp
    else:
        st.error("Token expired. Please reload the app and re-authenticate.")
        return None