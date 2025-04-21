from dotenv import load_dotenv
import os
from requests import post, get
import base64
import json 


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

#Getting access_token by sending encoded authorization
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(url, headers=headers, data=data)
    if result.status_code == 200:
        print("Access Token (JSON):\n")
        print((result.content))
        return json.loads(result.content)["access_token"]
    else:
        print("Token Error:", result.status_code, result.text)
        return None
    

#Organizing Bearer Header
def get_auth_header(token):
    return {"Authorization": "Bearer " + token} 

#Searching for a specific playlist
def search_playlists(token, query, limit=1):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    params = {
        "q": query,
        "type": "playlist",
        "limit": limit
    }
    response = get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Search failed: {response.status_code}")
        return []
    else:
        print("\n\nPlaylist Information (JSON): \n")
        print(response.content)
        return json.loads(response.content).get("playlists", {}).get("items", [])
    
#Getting 5 top tracks from a playlist
def get_playlist_tracks(token, playlist_id, limit=5):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = get_auth_header(token)
    params = {"limit": limit}
    response = get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch tracks: {response.status_code}")
        return []
    else:
        print("\n\nTracks (JSON): ")
        print (response.content)
        items = json.loads(response.content).get("items", [])
        valid_tracks = []
        for item in items:
            track = item.get("track")
            if track and track.get("id") and track.get("name"):  # sanity check
                valid_tracks.append(track)
        
        return valid_tracks
        