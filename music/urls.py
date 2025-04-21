from django.urls import path
from .views import PlaylistSearchView, search_playlist_html, show_lyrics, release_info, soundcloud_music_view

urlpatterns = [
    path('playlist-search/', PlaylistSearchView.as_view(), name='playlist-search'),
    path("playlist/search-form/", search_playlist_html, name="playlist-search-html"),
    path('track/<int:track_id>/', show_lyrics, name='track-lyrics'),
    path('release-info/<int:track_id>/', release_info, name='release_info'),
    path('soundcloud/music/', soundcloud_music_view, name='soundcloud-music'),
    path('lyrics/<int:track_id>/', show_lyrics, name='show_lyrics'),

]
