from . import models
from pprint import pprint


def get_user(spot):

    this_user = spot.current_user()
    spotify_user, \
    created = models.User.objects.get_or_create(spotify_id=this_user['id'])
    spotify_user.spotify_name = this_user['display_name']
    spotify_user.save()
    return spotify_user.spotify_name


def suck(spot):
    return get_user(spot)

