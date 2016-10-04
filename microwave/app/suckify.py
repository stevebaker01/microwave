from . import models
from datetime import timedelta
from dateutil.parser import parse as parse_date

# TODO: label support for albums
# TODO: external id support (which objects?)
# TODO: threading

TRACK_FIELDS = ['album', 'artists', 'duration_ms', 'external_ids',
                'external_urls', 'href', 'id', 'name', 'popularity', 'uri']
LIMITS = {'user_playlists': 50,
          'user_playlist_tracks': 100}


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
    # TODO: adding 'fields' to args returns empty query set. Spotipy bug?
    # fields = ','.join(TRACK_FIELDS)
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
    collection.label = album['label']
    collection.spotify_release = parse_date(album['release_date'])
    collection.spotify_type = album['type']
    return collection


def make_track(spotify_track):

    # make the track object
    duration = timedelta(milliseconds=spotify_track['duration_ms'])
    track = models.Track(spotify_id=spotify_track['id'],
                         spotify_name=spotify_track['name'],
                         spotify_duration=duration)
    # separate artists for later batching
    artists = dict((a['id'], a) for a in spotify_track['artists'])
    return track, spotify_track['album'], artists


def make_profile(spotify_track, spotify_profile):

    # trim fat
    skip = ['id', 'analysis_url', 'track_href', 'type', 'uri']
    profile = models.SpotifyProfile(id=spotify_profile['id'])
    profile.popularity = spotify_track['popularity']
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
    existing_genres = models.Genre.objects.filter(domain='spotify',
                                                  name__in=spotify_genres)
    name_existing = dict((g.name, g) for g in existing_genres)

    # create new genres
    new_genre_names = set(spotify_genres).difference(name_existing.keys())
    if new_genre_names:
        new_genres = []
        for new_genre in new_genre_names:
            new_genres.append(models.Genre(domain='spotify', name=new_genre))
        if new_genres:
            models.Genre.objects.bulk_create(new_genres)
            # appearantly after doing a bulk create django doesn't know the
            # objects hasve been written to the db.
            new_genres = models.Genre.objects.filter(domain='spotify',
                                                     name__in=new_genre_names)
            name_existing.update(dict((g.name, g) for g in new_genres))
    return name_existing


def update_composers_collections(artist_dict,
                                 existing_composer_dict,
                                 album_dict,
                                 existing_collection_dict,
                                 genres):


    # bulk create new composers
    composers = [make_composer(a) for a in artist_dict.values()]
    composers = models.Composer.objects.bulk_create(composers)
    comp_ids = set([composer.spotify_id for composer in composers])
    composers = models.Composer.objects.filter(spotify_id__in=comp_ids)
    composer_dict = dict((c.spotify_id, c) for c in composers)
    composer_dict.update(existing_composer_dict)

    # bulk create new collections
    collections = [make_collection(a) for a in album_dict.values()]
    collections = models.Collection.objects.bulk_create(collections)
    coll_ids = set([collection.spotify_id for collection in collections])
    collections = models.Collection.objects.filter(spotify_id__in=coll_ids)
    collection_dict = dict((c.spotify_id, c) for c in collections)
    collection_dict.update(existing_collection_dict)


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
    chunks = chunkify(ids, size)
    things = []
    plural = ('{}' if thing_type.endswith('s') else '{}s').format(thing_type)
    for chunk in chunks:
        these = getattr(spotipy, plural)(chunk)
        if thing_type != 'audio_features':
            things.extend(these[plural])
        else:
            things.extend(these)
    return dict((thing['id'], thing) for thing in things)


def assemble_composers_collections(artist_dict, album_dict, spotipy):

    # fetch existing (full) collection objects fron django
    existing_collections = models.Collection.objects.filter(spotify_id__in=
                                                            album_dict.keys())
    # fetch new (full) collection objects from spotify
    id_collections = dict((c.spotify_id, c) for c in existing_collections)
    new_album_ids = set(album_dict.keys()).difference(id_collections.keys())
    new_albums = fetch_spotify(new_album_ids, 'album', spotipy)

    # collect new album artists
    required_artist_ids = set(artist_dict.keys())
    for new_album in new_albums.values():
        for artist in new_album['artists']:
            required_artist_ids.add(artist['id'])

    existing_composers = models.Composer.objects.filter(spotify_id__in=
                                                        required_artist_ids)
    id_composers = dict((c.spotify_id, c) for c in existing_composers)
    # fetch new (full) artists from spotify
    new_artist_ids = set(required_artist_ids).difference(id_composers.keys())
    new_artists = fetch_spotify(new_artist_ids, 'artist', spotipy)
    # upodate genres, composers, and collections
    genres = update_genres(new_artists, new_albums)
    new_comps, new_colls = update_composers_collections(new_artists,
                                                        id_composers,
                                                        new_albums,
                                                        id_collections,
                                                        genres)
    # merge old and new
    id_composers.update(new_comps)
    id_collections.update(new_colls)
    return id_composers, id_collections


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


def update_profiles(spotify_tracks, spotipy):

    spotify_profiles = fetch_spotify(spotify_tracks.keys(),
                                     'audio_features',
                                     spotipy)
    profiles = []
    for profile_id, spotify_profile in spotify_profiles.items():
        spotify_profile['signature'] = spotify_profile.pop('time_signature')
        profile = make_profile(spotify_tracks[profile_id],
                               spotify_profile)
        profiles.append(profile)
    profiles = models.SpotifyProfile.objects.bulk_create(profiles)
    return dict((profile.id, profile) for profile in profiles)


def trackify(spotify_tracks, spotipy):

    # returns a dictionary of spotify track ids to microwave/django
    # track objects.
    spotify_artists = {}
    spotify_albums = {}
    new_tracks = []
    for spotify_id, spotify_track in spotify_tracks.items():
        track, spotify_album, these_artists = make_track(spotify_track)
        new_tracks.append(track)
        spotify_artists.update(these_artists)
        spotify_albums[spotify_album['id']] = spotify_album

    new_tracks = models.Track.objects.bulk_create(new_tracks)
    new_tracks = dict((track.spotify_id, track) for track in new_tracks)
    # bulk created items do not include a primary key and therefore must
    # be fetched after creation

    new_tracks = models.Track.objects.filter(spotify_id__in=new_tracks.keys())
    new_tracks = dict((t.spotify_id, t) for t in new_tracks)
    composers, collections = assemble_composers_collections(spotify_artists,
                                                            spotify_albums,
                                                            spotipy)
    profiles = update_profiles(spotify_tracks, spotipy)
    for spotify_id, spotify_track in spotify_tracks.items():
        track = new_tracks[spotify_id]
        artist_ids = [a['id'] for a in spotify_track['artists']]
        track.composers.set([composers[c] for c in artist_ids])
        track.collections.add(collections[spotify_track['album']['id']])
        track.spotify_profile = profiles[spotify_id]
        track.save()
    return new_tracks


# TODO: modularize this function
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
                remove.append(id_tracks[i])
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
                id_existing.update(new_tracks)
            et = [t for t in id_existing.values()]
            playlist.tracks.set(et)
            playlists.append(playlist)
    return playlists


def get_user_tracks(user, spotipy):

    #saved_tracks = get_user_saved_tracks(user, spotify)
    playlists = get_user_playlists(user, spotipy)
    for playlist in playlists:
        print(playlist.title)

def suck(spotipy):

    user = get_user(spotipy)
    tracks = get_user_tracks(user, spotipy)
    return user.spotify_name
