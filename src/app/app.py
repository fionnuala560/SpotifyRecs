from flask import Flask, redirect, request, render_template, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# In-memory user store
users = {}

class User(UserMixin):
    def __init__(self, spotify_id, token_info):
        self.id = spotify_id
        self.token_info = token_info
        self.recommended_tracks = []
        self.previous_track_ids = set()
        self.seen_artists = set()
        self.seen_albums = set()

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Get credentials from environment variables
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
SCOPE = "user-top-read user-read-private"

def get_sp_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=None,
        show_dialog=True
    )

# --- Routes ---
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/login")
def login():
    sp_oauth = get_sp_oauth()
    return redirect(sp_oauth.get_authorize_url())

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/callback")
def callback():
    sp_oauth = get_sp_oauth()
    code = request.args.get("code")

    try:
        token_info = sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]

        sp = spotipy.Spotify(auth=token_info["access_token"])
        spotify_id = sp.current_user()["id"]

        user = User(spotify_id, token_info)
        users[spotify_id] = user

        login_user(user)

        return redirect(url_for("dashboard"))

    except spotipy.exceptions.SpotifyOauthError as e:
        return f"Authentication Failed: {e.error_description}", 400

@app.route("/dashboard")
@login_required
def dashboard():
    token_info = current_user.token_info
    sp_oauth = get_sp_oauth()

    if sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
            current_user.token_info = token_info
        except spotipy.exceptions.SpotifyOauthError:
            logout_user()
            return redirect(url_for("index"))

    sp = spotipy.Spotify(auth=current_user.token_info["access_token"])

    top_tracks = []
    top_artists = []
    time_ranges = ["long_term", "medium_term", "short_term"]

    for time_range in time_ranges:
        top_tracks = sp.current_user_top_tracks(limit=10, time_range=time_range)["items"]
        top_artists = sp.current_user_top_artists(limit=10, time_range=time_range)["items"]
        if top_tracks and top_artists:
            break

    if not top_tracks or not top_artists:
        return render_template("dashboard.html", no_data=True)

    if not top_tracks or not top_artists:
        return render_template("dashboard.html", no_data=True)

    tracks = [
        {"name": t["name"], "artist": t["artists"][0]["name"],
         "img": t["album"]["images"][0]["url"] if t["album"]["images"] else ""}
        for t in top_tracks
    ]
    artists = [
        {"name": a["name"], "img": a["images"][0]["url"] if a["images"] else ""}
        for a in top_artists
    ]
    genres = list({g for a in top_artists for g in a.get("genres", [])})[:5]
    recs = current_user.recommended_tracks if current_user.recommended_tracks else None

    return render_template("dashboard.html", tracks=tracks, artists=artists, genres=genres, recs=recs)

@app.route("/recommendations", methods=["POST"])
@login_required
def recommendations():
    token_info = current_user.token_info
    sp_oauth = get_sp_oauth()

    if sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
            current_user.token_info = token_info
        except spotipy.exceptions.SpotifyOauthError:
            logout_user()
            return redirect(url_for("index"))

    sp = spotipy.Spotify(auth=current_user.token_info["access_token"])

    top_artists = sp.current_user_top_artists(limit=10, time_range="short_term")["items"]
    genres = list({g for a in top_artists for g in a.get("genres", [])})[:5]

    recs = []
    for g in genres:
        results = sp.search(q=f"genre:{g}", type="track", limit=10)
        for t in results["tracks"]["items"]:
            track_id = t["id"]
            artist_name = t["artists"][0]["name"]
            album_name = t["album"]["name"]

            if (track_id not in current_user.previous_track_ids and
                    artist_name not in current_user.seen_artists and
                    album_name not in current_user.seen_albums):

                recs.append({
                    "name": t["name"],
                    "artist": artist_name,
                    "url": t["external_urls"]["spotify"],
                    "img": t["album"]["images"][0]["url"] if t["album"]["images"] else ""
                })

                current_user.previous_track_ids.add(track_id)
                current_user.seen_artists.add(artist_name)
                current_user.seen_albums.add(album_name)

            if len(recs) >= 10:
                break
        if len(recs) >= 10:
            break

    current_user.recommended_tracks = recs
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    # Distinguish between production (Render) and local development
    is_production = os.environ.get('RENDER') == 'true'

    # Set host, port, and debug mode based on the environment
    if is_production:
        host = '0.0.0.0'  # Required for Render
        port = int(os.environ.get('PORT', 5000))
        debug = False
    else:
        host = '127.0.0.1' # Default for local development
        port = 5000
        debug = True

    app.run(host=host, port=port, debug=debug)
























































