from django.contrib import admin
from .models import Playlist, Track, PlaylistTrackMap, Artist, ArtistTrackMap, Lyric

admin.site.register(Playlist)
admin.site.register(Track)
admin.site.register(PlaylistTrackMap)
admin.site.register(Artist)
admin.site.register(ArtistTrackMap)
admin.site.register(Lyric)