from django.core.management.base import BaseCommand
from app import models, tubify, util
from pprint import pformat

DEVELOPER_KEY = 'AIzaSyBGRPJtxf8F9r1JjXCzCfq1AA44WlxHSlE'
API_SERVICE = 'youtube'
API_VERSION = 'v3'


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('spotify_user', type=str)

    def handle(self, *args, **options):

        print(options['spotify_user'])
        user = models.User.objects.get(spotify_id=options['spotify_user'])
        tracks = user.tracks.all()
        microwave_tube = {}
        tubes = []
        for track in tracks:
            youtube = tubify.get_youtube()
            ids = tubify.youtube_search(youtube, track)
            if not ids:
                continue
            videos = tubify.youtube_videos(youtube, ids)
            video = tubify.match_track(track, videos)
            if video:
                microwave_tube[track.id] = video['id']
                tubes[track.id] = tubify.make_youtube(video)
        if tubes:
            return models.Youtube.objects.bulk_create(tubes)

