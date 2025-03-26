from django.urls import path
from .views import PlaylistSearchView

urlpatterns = [
    path('playlist-search/', PlaylistSearchView.as_view(), name='playlist-search'),
]
