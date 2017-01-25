from django.db import models
from ..util import dictate

HTTPS_SPOTIFY = 'https://api.spotify.com/v1/'


class SpotifyGenre(models.Model):

    name = models.CharField(max_length=100,
                            unique=True,
                            db_index=True)


class SpotifyComposer(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    name = models.CharField(max_length=200, blank=True)
    genres = models.ManyToManyField(SpotifyGenre)

    def __str__(self):
        return self.name

    def uri(self):
        return 'spotify:artist:{}'.format(self.id)

    def url(self):
        return '{}artists/{}'.format(HTTPS_SPOTIFY, self.id)


class SpotifyCollection(models.Model):

    TYPE_CHOICES = (
        ('album', 'album'),
        ('single', 'single'),
        ('compilation', 'compilation')
    )
    id = models.CharField(primary_key=True,
                          max_length=100,
                          blank=True,
                          unique=True,
                          db_index=True)
    composers = models.ManyToManyField(SpotifyComposer)
    label = models.CharField(max_length=250, blank=True)
    genres = genres = models.ManyToManyField(SpotifyGenre)
    title = models.CharField(max_length=200, blank=True)
    release = models.DateField(blank=True)
    type = models.CharField(max_length=11,
                            blank=True,
                            choices=TYPE_CHOICES)
    upc = models.CharField(max_length=15, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)


class SpotifyProfile(models.Model):

    # basic fields
    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    isrc = models.CharField(max_length=12, blank=True)
    title = models.CharField(max_length=200, blank=True)
    collections = models.ManyToManyField(SpotifyCollection)
    composers = models.ManyToManyField(SpotifyComposer)
    duration = models.DurationField(blank=True)

    # audio features fields
    acousticness = models.FloatField(blank=True)
    danceability = models.FloatField(blank=True)
    energy = models.FloatField(blank=True)
    instrumentalness = models.FloatField(blank=True)
    key = models.PositiveSmallIntegerField(blank=True)
    liveness = models.FloatField(blank=True)
    loudness = models.FloatField(blank=True)
    mode = models.BooleanField(blank=True)
    popularity = models.PositiveSmallIntegerField(blank=True)
    signature = models.FloatField(blank=True)
    speechiness = models.FloatField(blank=True)
    tempo = models.FloatField(blank=True)
    valence = models.FloatField(blank=True)

    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title

    def uri(self):
        return 'spotify:track:{}'.format(self.spotify_id)

    def url(self):
        return '{}tracks/{}'.format(HTTPS_SPOTIFY, self.spotify_id)


class SpotifyPlaylist(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    title = models.CharField(max_length=250, blank=True)
    version = models.TextField(max_length=1000, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    tracks = models.ManyToManyField(SpotifyProfile)

    def count(self):
        return len(self.tracks)

    def __str__(self):
        return self.title


class SpotifyUser(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          blank=True,
                          unique=True,
                          db_index=True)
    name = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    playlists = models.ManyToManyField(SpotifyPlaylist)

    def __str__(self):
        return self.name

    def tracks(self):
        tracks = {}
        for playlist in self.playlists.all():
            tracks.update(dictate(playlist.tracks.all()))


