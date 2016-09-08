from django.db import models

DOMAIN_CHOICES = (
    ('spotify', 'spotify'),
)


class Identifier(models.Model):

    TYPE_CHOICES = (
        ('href', 'href'),
        ('id', 'id'),
        ('name', 'name'),
        ('uri', 'uri')
    )
    CLASS_CHOICES = (
        ('str', 'str'),
        ('int', 'int')
    )
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    identity = models.CharField(max_length=250)
    cls = models.CharField(max_length=3, default='str', choices=CLASS_CHOICES)

    def __str__(self):
        return self.identity

    def identify(self):
        return eval('{}(self.identifier)'.format(self.cls))


class Genre(models.Model):

    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    name = models.CharField(max_length=50)

    def __str__(self):
        return '{}: {}'.format(self.domain, self.name)


class Duration(models.Model):

    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    miliseconds = models.IntegerField()

    def __str__(self):
        return '{}: {}'.format(self.domain, self.miliseconds)


class AlbumType(models.Model):

    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    TYPE_CHOICES = (
        ('album', 'album'),
        ('single', 'single'),
        ('compilation', 'compilation')
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return '{}: {}'.format(self.domain, self.type)


class ReleaseDate(models.Model):

    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    date = models.DateField()

    def __str__(self):
        return '{}: {}'.format(self.domain, self.date.isoformat())


class Composer(models.Model):

    spotify_id = models.CharField(max_length=36)
    identifiers = models.ManyToManyField(Identifier)
    genres = models.ManyToManyField(Genre)


class Track(models.Model):

    spotify_id = models.CharField(max_length=36)
    identifiers = models.ManyToManyField(Identifier)
    composers = models.ManyToManyField(Composer)
    genres = models.ManyToManyField(Genre)

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


class Album(models.Model):

    spotify_id = models.CharField(max_length=36)
    identifiers = models.ManyToManyField(Identifier)
    types = models.ManyToManyField(AlbumType)
    genres = models.ManyToManyField(Genre)
    composers = models.ManyToManyField(Composer)
    tracks = models.ManyToManyField(Track)
    release_dates = models.ManyToManyField(ReleaseDate)


class Playlist(models.Model):

    spotify_id = models.CharField(max_length=36)
    identifiers = models.ManyToManyField(Identifier)
    domain = models.CharField(max_length=20)
    description = models.TextField(max_length=1500)
    version = models.CharField(max_length=20)
    tracks = models.ManyToManyField(Track)


class User(models.Model):

    spotify_id = models.CharField(max_length=36)
    identifiers = models.ManyToManyField(Identifier)
    playlists = models.ManyToManyField(Playlist)
