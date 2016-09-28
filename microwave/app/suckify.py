from . import models
from datetime import timedelta
from dateutil.parser import parse as parse_date

# TODO: label support for albums
# TODO: external id support (which objects?)

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


def get_genres(spotify_genres):

    # select existing genres
    existing = models.Genre.objects.filter(domain='spotify',
                                           name__in=spotify_genres)
    id_existing = dict((e['name'], e) for e in existing)

    # identify and create new genres if required
    new_names = set(spotify_genres).difference(id_existing.keys())
    new_genres = []
    for new_name in new_names:
        new_genre = models.Genre(domain='spotify', name=new_name)
    if new_genres:
        new_genres = models.Genre.objects.bulk_create(new_genres)
    # pack 'em up and ship 'em off
    return id_existing.update(dict((g.name, g) for g in new_genres))


def make_composer(artist):

    composer = models.Composer(spotify_id=artist['id'])
    composer.spotify_name = artist['name']
    return composer


def make_collection(album):

    collection = models.Collection(spotify_id=album['id'])
    collection.spotify_name = album['name']
    # TODO: ...
    # collection.label = artist['label']
    collection.spotify_release = parse_date(album['release_date'])
    collection.spotify_type = album['type']
    return collection


def batch_update(artist_dict, album_dict, spotipy):

    things = {'artists': artist_dict, 'albums': album_dict}
    old, new = {}, {}

    required_genres = set()
    for kind, objs in things.items():
        analog = 'collection' if kind == 'albums' else 'composer'

        # get existing microwave objects
        this_class = getattr(models, analog.title())
        existing = this_class.objects.filter(spotify_id__in=objs.keys())
        old[analog] = dict((e.spotify_id, e) for e in existing)

        # get new spotify objects and collect genres required for both
        # composers (artists) and colections (albums)
        new_ids = set(objs.keys()).difference(old[analog].keys())
        new[analog], spotify_genres, = get_new_spotify(kind, new_ids, spotipy)
        required_genres.update(spotify_genres)

    # batch make new composers and collections if required
    for kind, dictionary in new.items():
        function = globals()['make_{}'.format(kind)]
        for spotify_id, spotify_object in dictionary.items():
            dictionary[spotify_id] = function(spotify_object, required_genres)
        cls = getattr(models, kind.title())
        new_objects = cls.objects.bulk_create(dictionary.values())
        for new_object in new_objects:
            dictionary[new_object.spotify_id] = new_object
    these = {}
    for key in set(new.keys()).update(old.keys()):
        existing = old[key] if key in old else {}
        created = new[key] if key in new else {}
        these[key] = existing.update(created)
    return these

def get_new_spotify(kind, ids, spotipy):

    # batch get full objects from spotify
    new_spotifys = getattr(spotipy, kind)(ids)
    new_spotifys = new_spotifys[kind] if kind in new_spotifys else []
    new = {}
    genres = []
    for this in new_spotifys:
        # collect required genres
        genres.extend(this['genres'] if 'genres' in new_spotifys else [])
        new[this['id']] = this
    return new, genres


def trackify(spotify_tracks, spotipy):

    spotify_artists = {}
    spotify_albums = {}
    tracks = {}
    for spotify_id, spotify_track in spotify_tracks.items():
        track = models.Track(spotify_id=spotify_id,
                             spotify_name=spotify_track['name'],
                             spotify_duration=spotify_track['duration_ms'])
        tracks[spotify_id] = track
        these_artists = dict((a['id'], a) for a in spotify_track['artists'])
        spotify_artists.update(these_artists)
        spotify_albums[spotify_track['album']['id']] = spotify_track['album']
    composers, collections = batch_update(spotify_artists,
                                          spotify_albums,
                                          spotipy)


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
        if create or playlist.version != spotify_playlist['snapshot_id']:
            playlist.title = spotify_playlist['name']
            playlist.version = spotify_playlist['snapshot_id']
            playlist_tracks = playlist.tracks.all()
            id_tracks = dict((t.spotify_id, t) for t in playlist_tracks)
            spotify_tracks = get_user_playlist_contents(user,
                                                        spotify_playlist,
                                                        spotipy)
            id_spotify = dict((t['id'], t) for t in spotify_tracks)
            # remove tracks no longer in the spotify playlist
            remove = []
            for i in set(id_tracks.keys()).difference(id_spotify.keys()):
                remove.append(id_tracks(i))
            if remove:
                playlist.tracks.remove(*remove)
            # add new tracks
            existing_tracks = models.Track.objects.filter(spotify_id__in=
                                                          id_spotify.keys())
            id_existing = dict((x.spotify_id, x) for x in existing_tracks)
            new_spotify = {}
            for i in set(id_spotify.keys()).difference(id_existing.keys()):
                new_spotify[i] = id_spotify[i]
            if new_spotify:
                new_tracks = trackify(new_spotify, spotipy)
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
