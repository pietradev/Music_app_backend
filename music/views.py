from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Playlist, PlaylistTrackMap
from .serializers import TrackSerializer

# Create your views here.

class PlaylistSearchView(APIView):
    def get(self, request):
        # Captura o nome da playlist enviado via GET (ex: ?name=Brazilian)
        playlist_name = request.GET.get('name')

        if not playlist_name:
            return Response({'error': 'Please provide a playlist name.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Busca a playlist com base no nome (usando busca parcial)
            playlist = Playlist.objects.get(name__icontains=playlist_name)
        except Playlist.DoesNotExist:
            return Response({'error': 'Playlist not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Busca os tracks associados à playlist através do relacionamento
        track_links = PlaylistTrackMap.objects.filter(playlist=playlist).select_related('track')
        tracks = [link.track for link in track_links]

        # Serializa as faixas com seus artistas
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)