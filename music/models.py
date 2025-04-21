from django.db import models

# Creating table Playlist
class Playlist(models.Model):
    #defining its fields
    name = models.CharField(max_length=250)
    spotify_id = models.CharField(max_length=100)

    #we can exhibit the name of the playlist when we instantiate this object
    def __str__(self):
        return self.name

#Creating Tracks table
class Track(models.Model):
    title = models.CharField(max_length=255)
    spotify_id = models.CharField(max_length=100)
    popularity = models.IntegerField()

    def __str__(self):
        return self.title


#Creating playlist-track table
class PlaylistTrackMap(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('playlist', 'track')
    
    def __str__(self):
        return f"{self.playlist.name} - {self.track.title}"
    
class Artist(models.Model):
    name = models.CharField(max_length=255)
    spotify_id = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class ArtistTrackMap(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('artist', 'track')
    
    def __str__(self):
        return f"{self.artist.name} - {self.track.title}"
    

class Lyric(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='lyrics')
    artist_name = models.CharField(max_length=255)
    lyrics = models.TextField()

    class Meta:
        unique_together = ('track', 'artist_name')


class SoundCloudWidget(models.Model):
    track_id = models.BigIntegerField(unique=True)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    stream_url = models.TextField()
    artwork_url = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.artist}"


class Recommendation(models.Model):
    track = models.ForeignKey(SoundCloudWidget, on_delete=models.CASCADE, related_name='recommended_by')
    recommended_track = models.ForeignKey(SoundCloudWidget, on_delete=models.CASCADE, related_name='recommendations')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommend {self.recommended_track.title} for {self.track.title}"