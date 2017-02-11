from . import models
from . import suckify
from .util import dictate
from . import tubify
import spotipy


def spotify2track(spotify_profile):

    args = ('isrc', 'title', 'duration')
    kwargs = {arg: getattr(spotify_profile, arg) for arg in args}
    kwargs['spotify_profile'] = spotify_profile
    return models.Track(**kwargs)


def microwave_spotify(spotify_profiles):

    tracks = [spotify2track(profile) for profile in spotify_profiles]
    tracks = models.Track.objects.bulk_create(tracks)
    return dictate(tracks)


def ingest(spotify_token=None):

    if spotify_token:
        spotify_user = suckify.suck(spotipy.Spotify(spotify_token))
        spotify_profiles = spotify_user.tracks()
        args = {'spotify_profile__id__in': list(spotify_profiles.keys())}
        microwave_tracks = models.Track.objects.filter(**args)
        microwave_tracks = {t.spotify_profile_id: t for t in microwave_tracks}
        cold = []
        spotify_ids = set(list(spotify_profiles.keys()))
        microwave_ids = set(list(microwave_tracks.keys()))
        for spotify_id in spotify_ids:
            if spotify_id not in microwave_ids:
                cold.append(spotify_profiles[spotify_id])
                del spotify_profiles[spotify_id]
            else:
                microwave_ids.remove(spotify_id)
        if cold:
            # dedup
            hot_tracks = microwave_spotify(list(dictate(cold).values()))
            microwave_tracks.update(hot_tracks)
        tubify.tv_dinner(microwave_tracks.values())

