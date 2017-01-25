from . import models
from . import suckify
import spotipy


def ingest(spotify_token=None):

    accounts = {}
    if spotify_token:
        spotify_user = suckify.suck(spotipy.Spotify(spotify_token))

