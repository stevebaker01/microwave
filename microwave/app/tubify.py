from . import util
from apiclient.discovery import build
from isodate import parse_duration as iso
from app import models
from steves_utilities.normalizer import normalize_string
from datetime import  timedelta
from pprint import pformat

DEVELOPER_KEY = 'AIzaSyBGRPJtxf8F9r1JjXCzCfq1AA44WlxHSlE'
API_SERVICE = 'youtube'
API_VERSION = 'v3'


def get_youtube():

    return build(API_SERVICE, API_VERSION, developerKey=DEVELOPER_KEY)


def youtube_search(youtube, track):

    norm_title = normalize_string(track.spotify_name)
    composers = track.composers.all()
    norm_composer = normalize_string(composers[0].spotify_name)
    query = '"{}" "{}"'.format(norm_composer, norm_title)
    print('query: {}'.format(query))

    results = youtube.search().list(
        q=query,
        part='id',
        type='video'
    ).execute()
    return [item['id']['videoId'] for item in results.get('items', [])]

def youtube_videos(youtube, ids):

    results = youtube.videos().list(
        id=','.join(ids),
        part='snippet,contentDetails'
    ).execute()
    return util.dictate(results.get('items', []))


def match_track(track, videos):

    d = {i: iso(v['contentDetails']['duration']) for i, v in videos.items()}
    close = {}
    for i, duration in d.items():
        if duration <  track.spotify_duration:
            continue
        close[i] = duration - track.spotify_duration
    if close:
        closest = min([v for v in close.values()])
        return videos[list(close.keys())[list(close.values()).index(closest)]]


def make_youtube(youtube_video):

    duration = iso(youtube_video['contentDetails']['duration'])
    title = youtube_video['contentDetails']['title']
    return models.YoutubeProfile(id=youtube_video['id'],
                                 title=title,
                                 duration=duration)
