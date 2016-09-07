from . import models
from pprint import pprint


def get_user(spot):

    this = spot.current_user()
    user, created = models.User.objects.get_or_create(id=this['id'])
    user.name, user.url, user.uri = this['display_name'], this['href'], this['uri']
    user.save()
    return user


def get_saved_tracks(spot):

    tracks = spot.current_user_saved_tracks()
    for track in tracks:
        pass


def get_playlists(spot):

    get_saved_tracks(spot)


def suck(spot):
    user = get_user(spot)
    collections = get_playlists(spot)



