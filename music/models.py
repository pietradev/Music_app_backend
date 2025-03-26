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
class Tracks(models.Model):
    title = models.CharField(max_length=255)
    spotify_id = models.CharField(max_length=100)
    popularity = models.IntegerField()


#Creating playlist-track table
class PlaylistTrackmap(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Tracks, on_delete=models.CASCADE)


    
