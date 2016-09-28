from django.db import models
from datetime import datetime

DOMAIN_CHOICES = (('spotify', 'spotify'),)


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

    genres = models.ManyToManyField(Genre)
    spotify_id = models.CharField(max_length=100,
                                  blank=True,
                                  unique=True,
                                  db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    """
    TODO: Because I want to support multiple sources auto_now and
    auto_now_add will need to be removed and set per item once
    other sources are implemented. Currently spotify is the only
    metadata source so they can be set to true here.
    """
    spotify_created = models.DateTimeField(auto_now_add=True, blank=True)
    spotify_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.spotify_name if self.spotify_name else ''


class Collection(models.Model):

    SPOTIFY_TYPE_CHOICES = (
        ('album', 'album'),
        ('single', 'single'),
        ('compilation', 'compilation')
    )
    composers = models.ManyToManyField(Composer)
    genres = models.ManyToManyField(Genre)
    spotify_id = models.CharField(max_length=100,
                                  blank=True,
                                  unique=True,
                                  db_index=True)
    spotify_label = models.CharField(max_length=250, blank=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    spotify_release = models.DateField(blank=True)
    spotify_type = models.CharField(max_length=11, blank=True,
                                    choices=SPOTIFY_TYPE_CHOICES)
    """
    TODO: Because I want to support multiple sources auto_now and
    auto_now_add will need to be removed and set per item once
    other sources are implemented. Currently spotify is the only
    metadata source so they can be set to true here.
    """
    spotify_created = models.DateTimeField(auto_now_add=True, blank=True)
    spotify_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.spotify_name if self.spotify_name else ''


class SpotifyProfile(models.Model):

    id = models.CharField(max_length=100, primary_key=True, db_index=True)

    acousticiness = models.FloatField()
    durations = models.DurationField()
    dancibility = models.FloatField()
    energy = models.FloatField()
    instrumentalness = models.FloatField()
    key = models.PositiveSmallIntegerField()
    liveness = models.FloatField()
    loudness = models.FloatField()
    mode = models.BooleanField()
    popularity = models.PositiveSmallIntegerField()
    signature = models.FloatField()
    speechiness = models.FloatField()
    tempo = models.FloatField()
    valence = models.FloatField()
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return id


class Track(models.Model):

    collections = models.ManyToManyField(Collection)
    composers = models.ManyToManyField(Composer)
    spotify_duration = models.DurationField(blank=True)
    spotify_id = models.CharField(max_length=100,
                                  blank=True,
                                  unique=True,
                                  db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    spotify_profile = models.OneToOneField(SpotifyProfile, blank=True)
    """
    TODO: Because I want to support multiple sources auto_now and
    auto_now_add will need to be removed and set per item once
    other sources are implemented. Currently spotify is the only
    metadata source so they can be set to true here.
    """
    spotify_created = models.DateTimeField(auto_now_add=True, blank=True)
    spotify_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.spotify_name if self.spotify_name else ''


class Playlist(models.Model):

    domain = models.CharField(max_length=7,
                              choices=DOMAIN_CHOICES,
                              blank=False)
    domain_id = models.CharField(max_length=100, blank=False)
    title = models.CharField(max_length=250, blank=True)
    version = models.TextField(max_length=1000, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    tracks = models.ManyToManyField(Track)

    class Meta:
        unique_together = ('domain', 'domain_id')

    def count(self):
        return len(self.tracks)

    def __str__(self):
        return '{}: {}'.format(self.domain, self.domain_id)


class User(models.Model):

    spotify_id = models.CharField(max_length=100,
                                  blank=True,
                                  unique=True,
                                  db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    """
    TODO: Because I want to support multiple sources auto_now and
    auto_now_add will need to be removed and set per item once
    other sources are implemented. Currently spotify is the only
    metadata source so they can be set to true here.
    """
    spotify_created = models.DateTimeField(auto_now_add=True, blank=True)
    spotify_updated = models.DateTimeField(auto_now=True, blank=True)
    tracks = models.ManyToManyField(Track)

    def __str__(self):
        if self.spotify:
            return self.spotify_name
