# music/management/commands/test_recommendations.py

from django.core.management.base import BaseCommand
from music.utils.recommendations import get_top_k_similar_tracks
from music.models import Track

class Command(BaseCommand):
    help = 'Test recommendation system for a given track ID.'

    def add_arguments(self, parser):
        parser.add_argument('track_id', type=int, help='ID of the track to get recommendations for')

    def handle(self, *args, **kwargs):
        track_id = kwargs['track_id']
        recommended_ids = get_top_k_similar_tracks(track_id, k=5)

        if not recommended_ids:
            self.stdout.write(self.style.WARNING('No recommendations found.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Recommendations for Track ID {track_id}:'))
        for rec_id in recommended_ids:
            try:
                track = Track.objects.get(id=rec_id)
                self.stdout.write(f'  → {track.title} by {track.artist.display_name}')
            except Track.DoesNotExist:
                self.stdout.write(f'  → Track ID {rec_id} (not found)')
