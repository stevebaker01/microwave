from . import models
from . import suckify
import spotipy


def ingest(spotify_token=None):

    sources = {}
    if spotify_token:
        sources['spotify'], tracks = suckify.suck(spotipy.Spotify(spotify_token))

