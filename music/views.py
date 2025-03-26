from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from music.services.spotify_api import get_token, search_playlists, get_playlist_tracks
from music.repositories.spotify_repository import (
    save_playlist, save_track, save_artist,
    save_playlist_track_map, save_artist_track_map
)
from .models import Playlist, PlaylistTrackMap
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