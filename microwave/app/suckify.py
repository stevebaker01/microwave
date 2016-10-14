from . import models
from microwave.celery import stalk
from datetime import timedelta
from dateutil.parser import parse as parse_date
from steves_utilities.profiler import profile

# TODO: move from mysql to postgres and remove retrieval stage from creation
# TODO: optimize limits for albums, artists, audio features
# TODO: Resolve duplicate upc on collections and isrc on tracks weirdness
# TODO: asynchronous task queue
# TODO: No album labels or album genres (spotify or spotipy bug?)

TRACK_FIELDS = ['album', 'artists', 'duration_ms', 'external_ids',
                'external_urls', 'href', 'id', 'name', 'popularity', 'uri']
LIMITS = {'user_playlists': 50,
          'user_playlist_tracks': 100}


#TODO: move to personal utils
@stalk.task
def chunkify(input_list, chunk_size):

    input_list = list(input_list)
    chunks = []
    while input_list:
        this_chunk = set()
        for i in range(chunk_size):
            try:
                this_chunk.add(input_list.pop())
            except IndexError:
                break
        chunks.append(this_chunk)
    return chunks


def get_user(spotipy):

    # microwave current spotify user
    spotify_user = spotipy.current_user()
    kwargs = {'spotify_id': spotify_user['id']}
    this_user, created = models.User.objects.get_or_create(**kwargs)
    this_user.spotify_name = spotify_user['display_name']
    this_user.spotify = True
    this_user.save()
    return this_user


def get_user_saved_tracks(user, spotipy):

    pass


def get_playlist_contents(user, playlist, spotipy):

    # given a spotify playlist's json return a dict of spotify track ids
    # to spotify tracks' json
    limit = LIMITS['user_playlist_tracks']
    # TODO: adding 'fields' to args returns empty query set. Spotipy bug?
    # fields = ','.join(TRACK_FIELDS)
    list_id = playlist['id']
    offset = 0
    content_list = []
    while len(content_list) < int(playlist['tracks']['total']):
        kwargs = {'playlist_id': list_id, 'limit': limit, 'offset': offset}
        these_tracks = spotipy.user_playlist_tracks(user.spotify_id, **kwargs)
        content_list.extend(t['track'] for t in these_tracks['items'])
        offset += limit
    content_dict = dict((item['id'], item) for item in content_list)
    return content_dict


def get_genres(spotify_genres):

    # select existing genres
    existing = models.Genre.objects.filter(domain='spotify',
                                           name__in=spotify_genres)
    id_existing = dict((e['name'], e) for e in existing)

    # identify and create new genres if required
    new_names = set(spotify_genres).difference(id_existing.keys())
    new_genres = [models.Genre(domain='spotify', name=n) for n in new_names]
    if new_genres:
        new_genres = models.Genre.objects.bulk_create(new_genres)
    # pack 'em up and ship 'em off
    return id_existing.update(dict((g.name, g) for g in new_genres))


def make_composer(artist):

    # microwave artist -> composer
    composer = models.Composer(spotify_id=artist['id'])
    composer.spotify_name = artist['name']
    return composer


def make_collection(album):

    # microwave album -> collection
    collection = models.Collection(spotify_id=album['id'])
    collection.spotify_name = album['name']
    collection.label = album['label']
    collection.spotify_release = parse_date(album['release_date'])
    collection.spotify_type = album['album_type']
    if 'upc' in album['external_ids']:
        collection.upc = album['external_ids']['upc']
    return collection


def make_track(spotify_track):

    # make the track object
    duration = timedelta(milliseconds=spotify_track['duration_ms'])
    isrc = None
    if 'isrc' in spotify_track['external_ids']:
        isrc = spotify_track['external_ids']['isrc'].replace('-', '')
    track = models.Track(spotify_id=spotify_track['id'],
                         spotify_name=spotify_track['name'],
                         spotify_duration=duration,
                         isrc=isrc)
    # separate artists for later batching
    artists = dict((a['id'], a) for a in spotify_track['artists'])
    # return track, spotify (json) album, and spotify (json) artists
    return track, spotify_track['album'], artists


def make_profile(spotify_track, spotify_profile):

    # return a new profile object given a spotify (json) track and
    # spotify (json) "audio_features" object
    profile = models.SpotifyProfile(id=spotify_profile['id'])
    # take popularity from spotify track
    profile.popularity = spotify_track['popularity']
    # plug in values from spotify audio features (json)
    for attr in spotify_profile:
        if attr == 'duration_ms':
            duration_ms = spotify_profile['duration_ms']
            profile.duration = timedelta(milliseconds=duration_ms)
        else:
            setattr(profile, attr, spotify_profile[attr])
    return profile


def update_genres(*dicts):

    # collect genres from dictionaries
    spotify_genres = set()
    for d in dicts:
        for v in d.values():
            spotify_genres.update(v['genres'])
    # bulk get existing genre dict from django
    kwargs = {'domain': 'spotify', 'name__in': spotify_genres}
    existing_genres = models.Genre.objects.filter(**kwargs)
    name_existing = dict((g.name, g) for g in existing_genres)

    # create new genres
    new_genre_names = set(spotify_genres).difference(name_existing.keys())
    if new_genre_names:
        new_genres = []
        for new_genre in new_genre_names:
            new_genres.append(models.Genre(domain='spotify', name=new_genre))
        if new_genres:
            models.Genre.objects.bulk_create(new_genres)
            kwargs = {'domain': 'spotify', 'name__in': new_genre_names}
            new_genres = models.Genre.objects.filter(**kwargs)
            name_existing.update(dict((g.name, g) for g in new_genres))
    return name_existing


def batch_create(thing_type, spotify_dict, existing_dict):

    # bulk create new things (composers, collections)
    # get relevant make function from globals
    function = globals()['make_{}'.format(thing_type)]
    # get relevant microwave class
    cls = getattr(models, '{}'.format(thing_type.title()))
    # make things
    things = [function(a) for a in spotify_dict.values()]
    # bulk save things
    things = cls.objects.bulk_create(things)
    # re-retrieve things
    thing_ids = set([thing.spotify_id for thing in things])
    things = cls.objects.filter(spotify_id__in=thing_ids)
    # make new thing dict and integrate existing thing dict
    thing_dict = dict((c.spotify_id, c) for c in things)
    thing_dict.update(existing_dict)
    return thing_dict


def update_composers_collections(artist_dict, exist_comp_dict,
                                 album_dict, exist_coll_dict,genres):

    composer_dict = batch_create('composer', artist_dict, exist_comp_dict)
    collection_dict = batch_create('collection', album_dict, exist_coll_dict)

    # attach genres to new composers
    for spotify_id, spotify_artist in artist_dict.items():
        composer = composer_dict[spotify_id]
        composer.genres.set([genres[n] for n in spotify_artist['genres']])

    # attach composers and genres to new collections
    for spotify_id, spotify_album in album_dict.items():
        collection = collection_dict[spotify_id]
        collection.genres.set([genres[n] for n in spotify_album['genres']])
        album_comp_ids = [a['id'] for a in spotify_album['artists']]
        these = set([composer_dict[i] for i in album_comp_ids])
        collection.composers.set(these)

    # return happy new items
    return composer_dict, collection_dict


def fetch_spotify(ids, thing_type, spotipy):

    size = 20
    # make small chunks to retrieve
    chunks = chunkify(ids, size)
    things = []
    plural = ('{}' if thing_type.endswith('s') else '{}s').format(thing_type)
    for chunk in chunks:
        # request chunk
        these = getattr(spotipy, plural)(chunk)
        if thing_type != 'audio_features':
            things.extend(these[plural])
        else:
            things.extend(these)
    return dict((thing['id'], thing) for thing in things)


def assemble_collections(album_dict, artist_dict, spotipy):

    # fetch existing (full) collection objects fron django
    kwargs = {'spotify_id__in': album_dict.keys()}
    existing_collections = models.Collection.objects.filter(**kwargs)
    # fetch new (full) collection objects from spotify
    id_collections = dict((c.spotify_id, c) for c in existing_collections)
    new_album_ids = set(album_dict.keys()).difference(id_collections.keys())
    new_albums = fetch_spotify(new_album_ids, 'album', spotipy)

    # there are artists associatd with albums so let's find any of those that
    # might not be in the track artists
    required_artist_ids = set(artist_dict.keys())
    for new_album in new_albums.values():
        for artist in new_album['artists']:
            required_artist_ids.add(artist['id'])

    # return new spotify albums (json), existing collection dict, and a
    # list of spotify artist id required to satisfy both new tracks and their
    # albums.
    return new_albums, id_collections, required_artist_ids


def assemble_composers(required_artists, spotipy):

    # get existing composers
    kwargs = {'spotify_id__in': required_artists}
    existing_composers = models.Composer.objects.filter(**kwargs)
    id_composers = dict((c.spotify_id, c) for c in existing_composers)

    # get new artists from spotify
    new_artist_ids = set(required_artists).difference(id_composers.keys())
    new_artists = fetch_spotify(new_artist_ids, 'artist', spotipy)
    # return new spotify artist dict, and an existing composer dict
    return new_artists, id_composers


def assemble_composers_collections(artist_dict, album_dict, spotipy):

    # get
    args = (album_dict, artist_dict, spotipy)
    new_albums, id_collections, required_artists = assemble_collections(*args)
    new_artists, id_composers = assemble_composers(required_artists, spotipy)

    # upodate genres, composers, and collections
    genres = update_genres(new_artists, new_albums)
    args = (new_artists, id_composers, new_albums, id_collections, genres)
    new_composers, new_collections = update_composers_collections(*args)

    # merge old and new
    id_composers.update(new_composers)
    id_collections.update(new_collections)
    return id_composers, id_collections


def update_profiles(spotify_tracks, spotipy):

    # get audio features from spotify
    args = (spotify_tracks.keys(), 'audio_features', spotipy)
    spotify_profiles = fetch_spotify(*args)
    profiles = []
    # generate new microwave profiles
    for profile_id, spotify_profile in spotify_profiles.items():
        spotify_profile['signature'] = spotify_profile.pop('time_signature')
        profile = make_profile(spotify_tracks[profile_id], spotify_profile)
        profiles.append(profile)
    # save new profiles
    profiles = models.SpotifyProfile.objects.bulk_create(profiles)
    # return profile dict
    return dict((profile.id, profile) for profile in profiles)


def get_new_tracks(spotify_tracks, spotipy):

    # create new microwave tracks given spotify tracks (json)
    spotify_artists = {}
    spotify_albums = {}
    new_tracks = []
    for spotify_id, spotify_track in spotify_tracks.items():
        # make microwave track
        track, spotify_album, these_artists = make_track(spotify_track)
        new_tracks.append(track)
        spotify_artists.update(these_artists)
        spotify_albums[spotify_album['id']] = spotify_album
    # save retrieve and return new tracks, spotify (json) albums
    new_tracks = models.Track.objects.bulk_create(new_tracks)
    new_ids = [t.spotify_id for t in new_tracks]
    new_tracks = models.Track.objects.filter(spotify_id__in=new_ids)
    new_tracks = dict((t.spotify_id, t) for t in new_tracks)
    return spotify_artists, spotify_albums, new_tracks


def save_tracks(spotify_tracks, tracks, composers, collections, profiles):

    # sew tracks up with their composers, album, and profile
    saved_tracks = []
    for spotify_id, spotify_track in spotify_tracks.items():
        track = tracks[spotify_id]
        # associate composers
        artist_ids = [a['id'] for a in spotify_track['artists']]
        track.composers.set([composers[c] for c in artist_ids])
        # associate album
        track.collections.add(collections[spotify_track['album']['id']])
        # associate profile
        track.spotify_profile = profiles[spotify_id]
        track.save()
    return saved_tracks


def trackify(spotify_tracks, spotipy):

    # returns a dictionary of spotify track ids to microwave/django
    # track objects.
    # get new tracks (json) from spotify
    args = (spotify_tracks, spotipy)
    spotify_artists, spotify_albums, tracks = get_new_tracks(*args)
    args = (spotify_artists, spotify_albums, spotipy)
    # gather composers for new tracks
    composers, collections = assemble_composers_collections(*args)
    # create new profiles for new tracks
    profiles = update_profiles(spotify_tracks, spotipy)
    # gather collections for new tracks
    args = (spotify_tracks, tracks, composers, collections, profiles)
    return save_tracks(*args)


def update_playlist_tracks(spotify_tracks, playlist, spotipy):

    # add new tracks to playlist
    # get existing tracks
    kwargs = {'spotify_id__in': spotify_tracks.keys()}
    existing_tracks = models.Track.objects.filter(**kwargs)
    id_existing = dict((t.spotify_id, t) for t in existing_tracks)
    # identify new tracks
    new_spotify = {}
    for i in set(spotify_tracks.keys()).difference(id_existing.keys()):
        new_spotify[i] = spotify_tracks[i]
    # microwave new tracks
    if new_spotify:
        # microwave new tracks
        new_tracks = trackify(new_spotify, spotipy)
        # TODO: check this
        id_existing.update(new_tracks)
    playlist.tracks.set([t for t in id_existing.values()])
    return playlist


def update_playlist(spotify_playlist, user, spotipy):

    args = {'domain': 'spotify', 'domain_id': spotify_playlist['id']}
    playlist, create = models.Playlist.objects.get_or_create(**args)

    # is the playlist new or has it been modified?
    if create or playlist.version != spotify_playlist['snapshot_id']:

        # update the playlist
        playlist.title = spotify_playlist['name']
        playlist.version = spotify_playlist['snapshot_id']
        # get existing microwave tracks in playlist
        id_tracks = dict((t.spotify_id, t) for t in playlist.tracks.all())
        # get spotify tracks in playlist
        id_spotify = get_playlist_contents(user, spotify_playlist, spotipy)
        # update microwave playlist tracks
        args = (id_spotify, playlist, spotipy)
        playlist = update_playlist_tracks(*args)
        playlist.save()
    return playlist


@profile
def get_user_playlists(user, spotipy):

    # collect spotify user playlists
    limit = LIMITS['user_playlists']
    spotify_playlists = spotipy.user_playlists(user.spotify_id, limit=limit)
    total = int(spotify_playlists['total'])
    spotify_playlists = spotify_playlists['items']
    offset = 0
    while len(spotify_playlists) < total:
        offset += limit
        kwargs = {'limits': limit, 'offset': offset}
        these_playlists = spotipy.user_playlists(**kwargs)
        spotify_playlists.extend(these_playlists)

    # limit to playlists owned by the user
    spotify_playlists = [p for p in spotify_playlists
                         if p['owner']['id'] == user.spotify_id]

    # update and return microwave playlists
    updated = [update_playlist(p, user, spotipy) for p in spotify_playlists]
    return updated


def get_user_tracks(user, spotipy):

    #saved_tracks = get_user_saved_tracks(user, spotify)
    playlists = get_user_playlists(user, spotipy)


def suck(spotipy):

    user = get_user(spotipy)
    tracks = get_user_tracks(user, spotipy)
    return user.spotify_name
