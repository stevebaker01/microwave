from django.db import models
from .domain_models import spotify_models
from .domain_models import youtube_models


"""
class Genre(models.Model):

    domain = models.CharField(max_length=100,
                              choices=DOMAIN_CHOICES,
                              blank=False)
    name = models.CharField(max_length=50, blank=False)

    class Meta:
        unique_together = ('domain', 'name')

    def __str__(self):
        return '{}: {}'.format(self.domain, self.name)


class Composer(models.Model):

    name = models.CharField(max_length=200, blank=True)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.name


class Collection(models.Model):

    composers = models.ManyToManyField(Composer)
    genres = models.ManyToManyField(Genre)
    label = models.CharField(max_length=250, blank=True)
    name = models.CharField(max_length=200, blank=True)
    release = models.DateField(blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    upc = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name
"""

class Track(models.Model):

    isrc = models.CharField(max_length=12,
                            blank=True,
                            unique=True,
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
                                           blank=True,
                                           unique=True,
                                           db_index=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title


class User(models.Model):

    name = models.CharField(max_length=200, blank=True)
    spotify_user = models.OneToOneField(spotify_models.SpotifyUser, blank=True)
    youtube_user = models.OneToOneField(youtube_models.YoutubeUser, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    tracks = models.ManyToManyField(Track)

    def __str__(self):
        return self.name
