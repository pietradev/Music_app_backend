# music/services/soundcloud_api.py
import os
from dotenv import load_dotenv
import requests
from django.conf import settings

load_dotenv()

CLIENT_ID = os.getenv("SOUNDCLOUD_CLIENT_ID")
#CLIENT_ID = settings.SOUNDCLOUD_CLIENT_ID  # Set this in .env and settings.py

BASE_URL = "https://api-v2.soundcloud.com"
STREAM_BASE_URL = "https://api.soundcloud.com"

def search_soundcloud_tracks(query, limit=3):
    url = f"{BASE_URL}/search/tracks"
    params = {
        "q": query,
        "client_id": CLIENT_ID,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("collection", [])
    except requests.RequestException as e:
        print(f"SoundCloud API Error: {e}")
        return []

def build_stream_url(track_id):
    return f"{STREAM_BASE_URL}/tracks/{track_id}/stream?client_id={CLIENT_ID}"

def build_iframe_url(track_id):
    return (
        f"https://w.soundcloud.com/player/?url=https://api.soundcloud.com/tracks/{track_id}"
        "&auto_play=false&hide_related=true&show_comments=false"
        "&show_user=false&show_reposts=false&visual=true"
    )
