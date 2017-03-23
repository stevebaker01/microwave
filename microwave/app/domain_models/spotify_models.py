from django.db import models
from ..util import dictate

HTTPS_SPOTIFY = 'https://api.spotify.com/v1/'


class SpotifyGenre(models.Model):

    name = models.CharField(max_length=100, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)


class SpotifyComposer(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    genres = models.ManyToManyField(SpotifyGenre)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
    label = models.CharField(max_length=250, blank=True, null=True)
    genres = genres = models.ManyToManyField(SpotifyGenre)
    title = models.CharField(max_length=200, blank=True)
    release = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=11,
                            blank=True,
                            null=True,
                            choices=TYPE_CHOICES)
    upc = models.CharField(max_length=15, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class SpotifyProfile(models.Model):

    # basic fields
    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    isrc = models.CharField(max_length=12, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    collections = models.ManyToManyField(SpotifyCollection)
    composers = models.ManyToManyField(SpotifyComposer)
    duration = models.DurationField(blank=True, null=True)

    # audio features fields
    acousticness = models.FloatField(blank=True, null=True)
    danceability = models.FloatField(blank=True, null=True)
    energy = models.FloatField(blank=True, null=True)
    instrumentalness = models.FloatField(blank=True, null=True)
    key = models.PositiveSmallIntegerField(blank=True, null=True)
    liveness = models.FloatField(blank=True, null=True)
    loudness = models.FloatField(blank=True, null=True)
    mode = models.BooleanField(default=False)
    popularity = models.PositiveSmallIntegerField(blank=True, null=True)
    signature = models.FloatField(blank=True, null=True)
    speechiness = models.FloatField(blank=True, null=True)
    tempo = models.FloatField(blank=True, null=True)
    valence = models.FloatField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def uri(self):
        return 'spotify:track:{}'.format(self.spotify_id)

    def url(self):
        return '{}tracks/{}'.format(HTTPS_SPOTIFY, self.spotify_id)

    def genres(self):

        genres = []
        for collection in self.collections.all():
            for genre in collection.genres.all():
                genres.append(genre)
        return genres


class SpotifyPlaylist(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    title = models.CharField(max_length=250, blank=True, null=True)
    version = models.TextField(max_length=1000, blank=True, null=True)
    tracks = models.ManyToManyField(SpotifyProfile)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
    name = models.CharField(max_length=200, blank=True, null=True)
    playlists = models.ManyToManyField(SpotifyPlaylist)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    def tracks(self):
        tracks = {}
        for playlist in self.playlists.all():

            # for preserving my youtube data quota during testing
            if playlist.title != 'powertide':
                continue

            tracks.update(dictate(playlist.tracks.all()))
        return tracks
