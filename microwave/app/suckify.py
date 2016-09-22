from . import models
from datetime import timedelta
from dateutil.parser import parse as parse_date
from pprint import pprint


TRACK_FIELDS = ['album', 'artists', 'duration_ms', 'external_ids',
                'external_urls', 'href', 'id', 'name', 'popularity', 'uri']
LIMITS = {'user_playlists': 50,
          'user_playlist_tracks': 100}


def get_user(spotipy):

    spotify_user = spotipy.current_user()
    this_user, \
        created = models.User.objects.get_or_create(spotify_id=spotify_user['id'])
    this_user.spotify_name = spotify_user['display_name']
    this_user.spotify = True
    this_user.save()
    return this_user


def get_user_saved_tracks(user, spotipy):

    pass


def get_user_playlist_contents(user, playlist, spotipy):

    limit = LIMITS['user_playlist_tracks']
    fields = ','.join(TRACK_FIELDS)
    list_id = playlist['id']
    offset = 0
    contents = []
    while len(contents) < int(playlist['tracks']['total']):
        these_tracks = spotipy.user_playlist_tracks(user.spotify_id,
                                                    playlist_id=list_id,
                                                    limit=limit,
                                                    offset=offset)['items']
        contents.extend(t['track'] for t in these_tracks)
        offset += limit
    return contents


def get_genres(item):

    genres = []
    item = item['album'] if 'album' in item else item
    for spotify_genre in item['genres']:
        genre, created = models.Genre.objects.get_or_create(domain='spotify',
                                                            name=spotify_genre)
        if created:
            genre.save()
        genres.append(genre)
    return genres


def get_composers(item, spotipy):

    composers = []
    for artist in item['artists']:

        composer, created = models.Composer.objects.get_or_create(spotify_id=
                                                                  artist['id'])
        if created:
            artist = spotipy.artist(artist['id'])
            composer.spotify_name = artist['name']
            composer.save()
            composer.genres.add(*get_genres(artist))
            composer.save()
        composers.append(composer)

    return composers


def get_collection(album, spotipy):

    album = album['album'] if 'album' in album else album
    collection, created = models.Collection.objects.get_or_create(spotify_id=
                                                                  album['id'])
    if created:
        album = spotipy.album(album['id'])
        collection.publisher = album['label']
        collection.spotify_name = album['name']
        collection.spotify_release = parse_date(album['release_date'])
        collection.spotify_type = album['album_type']
        collection.save()
        collection.composers.add(*get_composers(album, spotipy))
        collection.genres.add(*get_genres(album))
        collection.save()
    return collection


def make_tracks(spotify_tracks, spotipy):

    tracks = []
    for spotify_track in spotify_tracks:

        duration = timedelta(milliseconds=spotify_track['duration_ms'])
        track, created = models.Track.objects.get_or_create(
            spotify_id=spotify_track['id'],
            spotify_name=spotify_track['name'],
            spotify_duration=duration
        )
        if created:
            track.save()
            track.composers.add(*get_composers(spotify_track, spotipy))
            track.collections.add(get_collection(spotify_track, spotipy))
            track.save()
            tracks.append(track)
    return tracks


def get_user_playlists(user, spotipy):

    limit = LIMITS['user_playlists']
    spotify_playlists = spotipy.user_playlists(user.spotify_id, limit=limit)
    total = int(spotify_playlists['total'])
    spotify_playlists = spotify_playlists['items']
    offset = 0
    while len(spotify_playlists) < total:
        offset += limit
        these_playlists = spotipy.user_playlists(user.spotify_id,
                                                 limits=limit,
                                                 offset=offset)
        spotify_playlists.extend(these_playlists)
    spotify_playlists = [p for p in spotify_playlists
                         if p['owner']['id'] == user.spotify_id]

    playlists = []
    for spotify_playlist in spotify_playlists:
        args = {'domain': 'spotify', 'domain_id': spotify_playlist['id']}
        playlist, create = models.Playlist.objects.get_or_create(**args)
        playlist.title = spotify_playlist['name']
        playlist.version = spotify_playlist['snapshot_id']
        spotify_tracks = get_user_playlist_contents(user,
                                                    spotify_playlist,
                                                    spotipy)
        playlist.save()
        playlist.tracks.add(*make_tracks(spotify_tracks, spotipy))
        playlist.save()
        playlists.append(playlist)
    return playlists


def get_user_tracks(user, spotipy):

    #saved_tracks = get_user_saved_tracks(user, spotify)
    playlists = get_user_playlists(user, spotipy)
    for playlist in playlists:
        print(playlist['name'])

def suck(spotipy):

    user = get_user(spotipy)
    tracks = get_user_tracks(user, spotipy)
    return user.spotify_name
