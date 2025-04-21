from rest_framework import serializers
from .models import Track, ArtistTrackMap, Playlist, PlaylistTrackMap

#Definin serializer to exhibit track information - artists, name, popularity
class TrackSerializer(serializers.ModelSerializer):
    artists = serializers.SerializerMethodField()

    class Meta:
        model = Track #model conneceted to Track
        fields = ['title', 'popularity', 'artists'] #fields that are going to be returned
    
    def get_artists(self, obj):
        artists_link = ArtistTrackMap.objects.filter(track=obj).select_related('artist')
        return [link.artist.name for link in artists_link]

