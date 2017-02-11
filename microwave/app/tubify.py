import re
from . import util
from datetime import timedelta
from django.db.utils import IntegrityError
from apiclient.discovery import build
from isodate import parse_duration as iso
from .domain_models import youtube_models
from steves_utilities.normalizer import normalize_string

DEVELOPER_KEY = 'AIzaSyC-epq05GzsgImwy_Z62oKDE4Ur06hOGSo'
API_SERVICE = 'youtube'
API_VERSION = 'v3'


def tv_dinner(tracks):

    youtube = get_youtube()
    for track in tracks:
        youtube_ids = youtube_search(youtube, track)
        if youtube_ids:
            video = get_youtube_video(track, youtube, youtube_ids)
            # video = make_youtube(match_track(track, these_videos))
            video.save()
            track.youtube_profile = video
            track.save()
            """
            try:
                track.save()
            except IntegrityError:
                pass
            """


def get_youtube():

    return build(API_SERVICE, API_VERSION, developerKey=DEVELOPER_KEY)


def youtube_search(youtube, track):

    composers = [c.name for c in track.spotify_profile.composers.all()]
    composers = ', '.join(composers)

    query = '{} {}'.format(track.title, composers)
    # query = re.sub(r'\W+', ' ', query)
    query = re.sub(r'\s+', ' ', query)

    video_duration = 'medium'
    if track.duration >= timedelta(minutes=20):
        video_duration = 'long'
    elif track.duration <= timedelta(minutes=4):
        video_duration = 'short'

    print('query: {}'.format(query))
    results = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        order='relevance'
    ).execute()
    return [item['id']['videoId'] for item in results.get('items', [])]


def get_youtube_video(track, youtube, youtube_ids):

    videos = get_youtube_videos(youtube, youtube_ids)
    videos = {v['id']: make_youtube(v) for v in videos}

    first = videos[youtube_ids[0]]
    fd, td = first.duration, track.duration
    diff = fd - td if fd > td else td - fd

    # if the first video looks to long or too short consider other videos
    if diff > timedelta(seconds=60):
        durations = {}
        youtube_ids.reverse()
        for i in youtube_ids:
            vd = videos[i].duration
            diff = vd - td if vd > td else td - vd
            durations[diff] = videos[i]
        return durations[min(list(durations.keys()))]
    return first



def get_youtube_videos(youtube, youtube_ids):

    ids = ','.join(youtube_ids)
    results = youtube.videos().list(
        id=ids,
        part='snippet,contentDetails'
    ).execute()
    these = results.get('items', [])
    return these
    # return util.dictate(results.get('items', []))


def match_track(track, videos):

    d = {i: iso(v['contentDetails']['duration']) for i, v in videos.items()}
    close = {}
    for i, duration in d.items():
        if duration < track.duration:
            continue
        close[i] = duration - track.duration
    if close:
        closest = min([v for v in close.values()])
        return videos[list(close.keys())[list(close.values()).index(closest)]]


def make_youtube(youtube_video):

    duration = iso(youtube_video['contentDetails']['duration'])

    title = youtube_video['snippet']['title']
    return youtube_models.YoutubeProfile(id=youtube_video['id'],
                                         title=title,
                                         duration=duration)
