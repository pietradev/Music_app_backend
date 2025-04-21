from music.models import Playlist, Track, Artist, PlaylistTrackMap, ArtistTrackMap

def save_playlist(data):
    playlist, _ = Playlist.objects.get_or_create(
        spotify_id=data['id'],
        defaults={
            'name': data['name']
        }
    )
    return playlist


def save_track(data):
    track, _ = Track.objects.get_or_create(
        spotify_id=data['id'],
        defaults={
            'title': data['name'],
            'popularity': data.get('popularity', 0)
        }
    )
    return track


def save_artist(data):
    artist, _ = Artist.objects.get_or_create(
        spotify_id=data['id'],
        defaults={
            'name': data['name']
        }
    )
    return artist


def save_playlist_track_map(playlist, track):
    PlaylistTrackMap.objects.get_or_create(
        playlist=playlist,
        track=track
    )


def save_artist_track_map(artist, track):
    ArtistTrackMap.objects.get_or_create(
        artist=artist,
        track=track
    )
