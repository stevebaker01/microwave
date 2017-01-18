from django.db import models


class YoutubeProfile(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    title = models.CharField(max_length=200)
    duration = models.DurationField()

    def __str__(self):
        return self.title


class YoutubePlaylist(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          unique=True,
                          db_index=True)
    title = models.CharField(max_length=250, blank=True)
    version = models.TextField(max_length=1000, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    videos = models.ManyToManyField(YoutubeProfile)

    def count(self):
        return len(self.videos)

    def __str__(self):
        return self.title


class YoutubeUser(models.Model):

    id = models.CharField(primary_key=True,
                          max_length=100,
                          blank=True,
                          unique=True,
                          db_index=True)
    name = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    tracks = models.ManyToManyField(YoutubeProfile)

    def __str__(self):
        return self.name
