from music.models import Lyric

def insert_or_update_lyric(track, artist_name: str, lyrics: str):
    lyric, _ = Lyric.objects.update_or_create(
        track=track,
        defaults={"artist_name": artist_name, "lyrics": lyrics}
    )
    return lyric
