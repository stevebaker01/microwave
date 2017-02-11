from django.core.management.base import BaseCommand
from ...models import spotify_models as spotify


class Command(BaseCommand):

    def handle(self, *args, **options):
        me = spotify.SpotifyUser.objects.get(id='121529524')
        profiles = me.tracks()
        elastic_profiles = []
        fields = [f.name for f in spotify.SpotifyProfile._meta.get_fields()]
        for field in fields:
            print(field)
