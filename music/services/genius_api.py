import os
import lyricsgenius
from music.models import Track, ArtistTrackMap
from music.repositories.genius_repository import insert_or_update_lyric 

# Setup Genius API client
genius_token = os.getenv("GENIUS_TOKEN")
genius = lyricsgenius.Genius(genius_token, timeout=30)

def fetch_lyrics_from_genius(track_title: str, artist_name: str):
    """
    Fetch lyrics using Genius API.
    """

    song = genius.search_song(track_title, artist_name)
    if song and song.lyrics:
        return song.lyrics
    return None


def fetch_and_store_lyrics(track_id: int, artist_name: str):
    """
    Given a Track ID, fetch lyrics and save them to DB using the first related artist.
    """
    try:
        track = Track.objects.get(id=track_id)
    except Track.DoesNotExist:
        return None, "Track not found"
    
    artist_map = ArtistTrackMap.objects.filter(track=track).first()
    if not artist_map:
        return None, "No artist found for this track"

    artist_name = artist_map.artist.name
    lyrics = fetch_lyrics_from_genius(track.title, artist_name)

    if lyrics:
        lyric_obj = insert_or_update_lyric(track, artist_name, lyrics)
        return lyric_obj, None
    else:
        return None, "Lyrics not found on Genius"


