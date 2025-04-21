import os
import requests
from dotenv import load_dotenv

load_dotenv()
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")

def get_track_data(query):
    url = "https://api.discogs.com/database/search"
    params = {
        "q": query,
        "token": DISCOGS_TOKEN,
        "type": "release"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Discogs API Error {response.status_code}: {response.text}")
        return []
