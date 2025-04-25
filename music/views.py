from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q 
from music.services.spotify_api import get_token, search_playlists, get_playlist_tracks
from music.services.genius_api import fetch_and_store_lyrics
from music.services.discogs_api import get_track_data
from music.repositories.discogs_repository import fetch_release_info_for_track
from music.services.soundcloud_api import *
from music.repositories.spotify_repository import (
    save_playlist, save_track, save_artist,
    save_playlist_track_map, save_artist_track_map
)
from .models import Playlist, PlaylistTrackMap, Track, Lyric, ArtistTrackMap, SoundCloudWidget, Metadata
from .serializers import TrackSerializer

from dotenv import load_dotenv
import os

load_dotenv()

# Create your views here.


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

if not client_id or not client_secret:
    raise Exception("CLIENT_ID or CLIENT_SECRET not found. Check your .env file and variable names.")

class PlaylistSearchView(APIView):
    def get(self, request):
        # Captura o nome da playlist enviado via GET (ex: ?playlistName=Brazilian)
        playlist_name = request.GET.get('playlistName')

        if not playlist_name:
            return Response({'error': 'Please provide a playlist name.'}, status=status.HTTP_400_BAD_REQUEST)
            #We are going to use Spotify Service, find a new playlist, and add the data to the db


        try:
            # search for the playlist in the db
            playlist = Playlist.objects.get(name__icontains=playlist_name)
        except Playlist.DoesNotExist:
            # Not found in DB → Use Spotify API
            token = get_token()
            if not token:
                return Response({'error': 'Failed to authenticate with Spotify'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            playlists = search_playlists(token, playlist_name, limit=1)
            if not playlists:
                return Response({'error': 'No playlists found on Spotify'}, status=status.HTTP_404_NOT_FOUND)

            # Save the first Spotify playlist found
            playlist_data = playlists[0]
            playlist = save_playlist(playlist_data)

            # Fetch and save tracks
            tracks = get_playlist_tracks(token, playlist_data['id'], limit=5)

            for track_data in tracks:
                track = save_track(track_data)
                save_playlist_track_map(playlist, track)

                for artist_data in track_data.get('artists', []):
                    artist = save_artist(artist_data)
                    save_artist_track_map(artist, track)

            print(Response({
                'message': f"Playlist '{playlist.name}' was fetched from Spotify and saved.",
                'playlist_id': playlist.id,
                'tracks_saved': len(tracks)
            }, status=status.HTTP_201_CREATED))

        # Busca os tracks associados à playlist através do relacionamento
        track_links = PlaylistTrackMap.objects.filter(playlist=playlist).select_related('track')
        tracks = [link.track for link in track_links]

        # Serializa as faixas com seus artistas
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)
    


def search_playlist_html(request):
    playlist_name = request.GET.get("playlistName")
    context = {}

    if playlist_name:
        try:
            playlist = Playlist.objects.get(name__icontains=playlist_name)
        except Playlist.DoesNotExist:
            token = get_token()

            if not token:
                context["message"] = "Error retrieving Spotify token."
                return render(request, "index.html", context)
        
            playlists = search_playlists(token, playlist_name)

            if not playlists:
                context["message"] = f"No playlists found for '{playlist_name}'."
                return render(request, "index.html", context)
            
            if playlists:
                playlist_data = playlists[0]

                if not playlist_data:
                    context["message"] = f"Invalid playlist data received from Spotify for '{playlist_name}'."
                    return render(request, "index.html", context)
            
                playlist = save_playlist(playlist_data)
                tracks = get_playlist_tracks(token, playlist_data["id"])

                for track_data in tracks:
                    track = save_track(track_data)
                    save_playlist_track_map(playlist, track)
                    for artist_data in track_data.get("artists", []):
                        artist = save_artist(artist_data)
                        save_artist_track_map(artist, track)

        # Buscar as faixas no banco
        track_links = PlaylistTrackMap.objects.filter(playlist=playlist).select_related("track")
        tracks = [link.track for link in track_links]
        context["tracks"] = tracks
    else:
        context["message"] = "Type in the name of your playlist."

    return render(request, "index.html", context)



def show_lyrics(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    lyrics_obj = track.lyrics.first()

    if not lyrics_obj:
        artist_map = track.artisttrackmap_set.first()
        artist_name = artist_map.artist.name if artist_map else None

        if not artist_name:
            return render(request, "lyrics.html", {
                "track": track,
                "error": "No artist found for this track."
            })

        lyrics_obj, error = fetch_and_store_lyrics(track_id, artist_name)
        if error:
            return render(request, "lyrics.html", {
                "track": track,
                "error": error
            })
        
    lyrics = lyrics_obj.lyrics # Ensure you are getting the string

    # Apply split or slicing if necessary
    if lyrics:
        intro_start_index = lyrics.find("[")
        if intro_start_index != -1:
            lyrics = lyrics[intro_start_index:]

    return render(request, "lyrics.html", {
        "track": track,
        "lyrics": lyrics
    })

def soundcloud_music_view(request):
    title = request.GET.get('title')
    artist = request.GET.get('artist')
    search_term = f"{title} {artist}"
    
    sc_tracks = search_soundcloud_tracks(search_term, limit=3)

    result_tracks = []

    for track in sc_tracks:
        if track.get("streamable"):
            track_id = track["id"]
            title = track["title"]
            artist = track["user"]["username"]
            artwork_url = track.get("artwork_url", "")
            stream_url = build_stream_url(track_id)
            iframe_url = build_iframe_url(track_id)

            # Optional: store in your Track model if desired
            SoundCloudWidget.objects.get_or_create(
                title=title,
                artist=artist,
                defaults={
                    "track_id": track_id,
                    "stream_url": stream_url,
                    "artwork_url": artwork_url,
                }
            )

            result_tracks.append({
                "title": title,
                "artist": artist,
                "artwork_url": artwork_url,
                "iframe_url": iframe_url,
                "track_id": track_id,
            })

    return render(request, "music.html", {"tracks": result_tracks})

def release_info(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    release, error = fetch_release_info_for_track(track)

    context = {
        "track": track,
        "release": release,
        "error": error
    }

    return render(request, "track-info.html", context)