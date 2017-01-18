import os
# import spotipy
from . import ingest
from spotipy import oauth2
from django.http import HttpResponse, JsonResponse
from pprint import pprint


PORT_NUMBER = 8000
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REDIRECT_URI = 'http://localhost:8000'
SCOPE = 'playlist-read-private'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
                                scope=SCOPE,cache_path=CACHE)

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
        return HttpResponse(results)
    else:
        return HttpResponse(htmlForLoginButton())


def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url
