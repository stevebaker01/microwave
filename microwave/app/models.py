from django.db import models

DOMAIN_CHOICES = (('spotify', 'spotify'),)


class Genre(models.Model):

    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES,
                              blank=False)
    name = models.CharField(max_length=50, blank=False)

    class Meta:
        unique_together = ('domain', 'name')

    def __str__(self):
        return '{}: {}'.format(self.domain, self.name)


class Composer(models.Model):

    spotify = models.BooleanField(default=False)
    spotify_id = models.CharField(max_length=20, blank=True, unique=True,
                                  db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        if self.spotify:
            return self.spotify_name


class Collection(models.Model):

    SPOTIFY_TYPE_CHOICES = (
        ('album', 'album'),
        ('single', 'single'),
        ('compilation', 'compilation')
    )
    composers = models.ManyToManyField(Composer)
    genres = models.ManyToManyField(Genre)
    spotify = models.BooleanField(default=False)
    spotify_id = models.CharField(max_length=20, blank=True, unique=True,
                                  db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    spotify_release = models.DateField(blank=True)
    spotify_type = models.CharField(max_length=11, blank=True,
                                    choices=SPOTIFY_TYPE_CHOICES)

    def __str__(self):
        if self.spotify:
            return self.spotify_name


class SpotifyProfile(models.Model):

    id = models.CharField(max_length=20, primary_key=True, db_index=True)

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

    def __str__(self):
        return id


class Track(models.Model):

    collections = models.ManyToManyField(Collection)
    composers = models.ManyToManyField(Composer)
    genres = models.ManyToManyField(Genre)
    spotify = models.BooleanField(default=False)
    spotify_durration = models.DurationField(blank=True)
    spotify_id = models.CharField(max_length=20, blank=True,
                                  unique=True, db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    spotify_profile = models.OneToOneField(SpotifyProfile)

    def __str__(self):
        if self.spotify:
            return self.spotify_name


class Playlist(models.Model):

    domain = models.CharField(max_length=7, choices=DOMAIN_CHOICES,
                              blank=False)
    domain_id = models.CharField(max_length=100, blank=False)
    title = models.CharField(max_length=250, blank=True)
    summary = models.TextField(max_length=2500, blank=True)
    tracks = models.ManyToManyField(Track)

    class Meta:
        unique_together = ('domain', 'domain_id')

    def __str__(self):
        return '{}: {}'.format(self.domain, self.domain_id)


class User(models.Model):

    spotify = models.BooleanField(default=False)
    spotify_id = models.CharField(max_length=20, blank=True,
                                  unique=True, db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    tracks = models.ManyToManyField(Track)

    def __str__(self):
        if self.spotify:
            return self.spotify_name
