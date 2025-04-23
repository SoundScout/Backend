# music/management/commands/generate_recommendations.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from playlists.models import Recommendation
from music.models import TrackFeature
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

User = get_user_model()

class Command(BaseCommand):
    help = "Generate personalized recommendations for all users."

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        track_features = TrackFeature.objects.select_related('track').all()

        # ✅ Build the matrix of all track embeddings
        track_embeddings = []
        track_ids = []

        for tf in track_features:
            if tf.embedding:
                track_embeddings.append(tf.embedding)
                track_ids.append(tf.track.id)

        if not track_embeddings:
            self.stdout.write(self.style.WARNING('No embeddings found.'))
            return

        track_embeddings = np.array(track_embeddings)

        for user in users:
            liked_tracks = user.interactions.filter(interaction_type='like').values_list('track_id', flat=True)

            if not liked_tracks:
                continue

            # ✅ Build user preference vector
            liked_embeddings = []
            for track_id in liked_tracks:
                try:
                    idx = track_ids.index(track_id)
                    liked_embeddings.append(track_embeddings[idx])
                except ValueError:
                    continue

            if not liked_embeddings:
                continue

            liked_embeddings = np.array(liked_embeddings)
            user_profile = np.mean(liked_embeddings, axis=0).reshape(1, -1)

            # ✅ Calculate similarity to all tracks
            similarities = cosine_similarity(user_profile, track_embeddings).flatten()

            # ✅ Get top 10 recommendations (excluding already liked)
            top_indices = similarities.argsort()[::-1]
            recommended_track_ids = []
            for idx in top_indices:
                track_id = track_ids[idx]
                if track_id not in liked_tracks:
                    recommended_track_ids.append(track_id)
                if len(recommended_track_ids) == 10:
                    break

            # ✅ Save to Recommendation table
            Recommendation.objects.update_or_create(
                user=user,
                defaults={'recommended_track_ids': recommended_track_ids}
            )

        self.stdout.write(self.style.SUCCESS('✅ Recommendations generated successfully!'))

