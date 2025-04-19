from django.urls import path
from .views import PlaylistSearchView, search_playlist_html, show_lyrics, soundcloud_music_view

urlpatterns = [
    path('playlist-search/', PlaylistSearchView.as_view(), name='playlist-search'),
    path("playlist/search-form/", search_playlist_html, name="playlist-search-html"),
    path('track/<int:track_id>/', show_lyrics, name='track-lyrics'),
    path('soundcloud/music/', soundcloud_music_view, name='soundcloud-music'),

]
