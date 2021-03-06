import os
# import spotipy
from . import ingest
from spotipy import oauth2
from django.http import HttpResponse, JsonResponse
from pprint import pprint


PORT_NUMBER = 8000
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI = 'http://localhost:8000/'
SPOTIFY_SCOPE = 'playlist-read-private'
SPOTIFY_CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID,
                               SPOTIFY_CLIENT_SECRET,
                               SPOTIFY_REDIRECT_URI,
                               scope=SPOTIFY_SCOPE,
                               cache_path=SPOTIFY_CACHE)


def index(request):
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.build_absolute_uri()
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:

        print("Spotify access token available! Trying to get user information...")

        tracks = ingest.ingest(spotify_token=access_token)
        #results = suckify.suck(spotipy.Spotify(access_token))

        #results = sp.user_playlists(sp.current_user()['id'])
        #pprint(results.keys())
        return HttpResponse('hi')
    else:
        return HttpResponse(htmlForLoginButton())


def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url
