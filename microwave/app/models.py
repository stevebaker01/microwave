from django.db import models


DOMAIN_CHOICES = (('spotify', 'spotify'),)
FORMAT_CHOICES = (('acc', 'acc'),
                  ('mp3', 'mp3'),
                  ('mp4', 'mp4'),
                  ('wav', 'wav'),
                  ('vorbis', 'vorbis'))
HTTPS_SPOTIFY = 'https://api.spotify.com/v1/'


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

    def __str__(self):
        return self.spotify_name if self.spotify_name else ''

    def spotify_uri(self):
        return 'spotify:artist:{}'.format(self.spotify_id)

    def spotify_url(self):
        return '{}artists/{}'.format(HTTPS_SPOTIFY, self.spotify_id)


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
    # Duplicate albums?? Look for dupicate upc codes on collections
    upc = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.spotify_name if self.spotify_name else ''

    def spotify_uri(self):
        return 'spotify:album:{}'.format(self.spotify_id)

    def spotify_url(self):
        return '{}albums/{}'.format(HTTPS_SPOTIFY, self.spotify_id)


class SpotifyProfile(models.Model):

    id = models.CharField(max_length=100, primary_key=True, db_index=True)

    acousticness = models.FloatField(blank=True)
    danceability = models.FloatField(blank=True)
    duration = models.DurationField(blank=True)
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
        return self.id


class YoutubeProfile(models.Model):

    id = models.CharField(max_length=11, primary_key=True)
    title = models.CharField(max_length=200)
    duration = models.DurationField()

    def __str__(self):
        return self.title


class Track(models.Model):

    collections = models.ManyToManyField(Collection)
    composers = models.ManyToManyField(Composer)
    # Duplicate tracks?? Look for dupicate isrc codes on tracks
    isrc = models.CharField(max_length=12, blank=True)
    spotify_duration = models.DurationField(blank=True)
    spotify_id = models.CharField(max_length=100,
                                  blank=True,
                                  unique=True,
                                  db_index=True)
    spotify_name = models.CharField(max_length=200, blank=True)
    # spotify_profile = models.OneToOneField(SpotifyProfile, blank=True)
    """
    TODO: Because I want to support multiple sources auto_now and
    auto_now_add will need to be removed and set per item once
    other sources are implemented. Currently spotify is the only
    metadata source so they can be set to true here.
    """
    spotify_created = models.DateTimeField(auto_now_add=True, blank=True)
    spotify_updated = models.DateTimeField(auto_now=True, blank=True)
    youtube_profile = models.OneToOneField(YoutubeProfile, blank=True)

    def __str__(self):
        return self.spotify_name if self.spotify_name else ''

    def spotify_uri(self):
        return 'spotify:track:{}'.format(self.spotify_id)

    def spotify_url(self):
        return '{}tracks/{}'.format(HTTPS_SPOTIFY, self.spotify_id)


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
        return self.spotify_name
