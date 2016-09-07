from django.db import models


class DomainAttribute(models.Model):

    DOMAIN_CHOICES = (
        ('spotify', 'spotify'),
    )
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)


class Identifier(DomainAttribute):

    TYPE_CHOICES = (
        ('id', 'id'),
        ('name', 'name'),
        ('href', 'href'),
        ('uri', 'uri')
    )
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    identity = models.CharField(max_length=250)
    cls = models.CharField(max_length=3, default='str')

    def __str__(self):
        return self.identity

    def identify(self):
        return eval('{}(self.identifier)'.format(self.cls))


class Genre(DomainAttribute):

    name = models.CharField(max_length=50)

    def __str__(self):
        return '{}: {}'.format(self.domain, self.name)


class Duration(DomainAttribute):

    miliseconds = models.IntegerField()

    def __str__(self):
        return '{}: {}'.format(self.domain, self.miliseconds)


class AlbumType(DomainAttribute):

    ALBUM_TYPE_CHOICES = (
        ('album', 'album'),             # spotify
        ('single', 'single'),           # spotify
        ('compilation', 'compilation')  # spotify
    )
    type = models.CharField(max_length=20, choices=ALBUM_TYPE_CHOICES)

    def __str__(self):
        return '{}: {}'.format(self.domain, self.type)


class ReleaseDate(DomainAttribute):

    date = models.DateField()

    def __str__(self):
        return '{}: {}'.format(self.domain, self.date.isoformat())


class Base(models.Model):

    spotify_id = models.CharField(max_length=36)
    identifiers = models.ManyToManyField(Identifier)

    def identify(self, type, domain):
        for identifier in self.identifiers:
            if identifier.type == type and identifier.domain == domain:
                return identifier.identity()


class Composer(Base):

    genres = models.ManyToManyField(Genre)


class Track(Base):

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


class Album(Base):

    types = models.ManyToManyField(AlbumType)
    genres = models.ManyToManyField(Genre)
    composers = models.ManyToManyField(Composer)
    tracks = models.ManyToManyField(Track)
    release_dates = models.ManyToManyField(ReleaseDate)


class Playlist(models.Model):

    identifiers = models.ManyToManyField(Identifier)
    domain = models.CharField(max_length=20)
    description = models.TextField(max_length=1500)
    version = models.CharField(max_length=20)
    tracks = models.ManyToManyField(Track)


class User(Base):

    playlists = models.ManyToManyField(Playlist)

