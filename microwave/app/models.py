from django.db import models
from .domain_models import spotify_models
from .domain_models import youtube_models


class Track(models.Model):

    isrc = models.CharField(max_length=12,
                            blank=True,
                            db_index=True)
    title = models.CharField(max_length=200, blank=True)
    duration = models.DurationField(blank=True)

    # Profiles
    spotify_profile = models.OneToOneField(spotify_models.SpotifyProfile,
                                           max_length=100,
                                           blank=True,
                                           unique=True,
                                           db_index=True)
    youtube_profile = models.OneToOneField(youtube_models.YoutubeProfile,
                                           max_length=11,
                                           blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title


class User(models.Model):

    name = models.CharField(max_length=200, blank=True)
    spotify_user = models.OneToOneField(spotify_models.SpotifyUser, blank=True)
    youtube_user = models.OneToOneField(youtube_models.YoutubeUser, blank=True)
    playlists = models.ManyToManyField(youtube_models.YoutubePlaylist,
                                       blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    tracks = models.ManyToManyField(Track)

    def __str__(self):
        return self.name
