import os
from celery import shared_task
import subprocess
from music.models import Track, TrackFeature
from music.utils.feature_extraction import extract_features

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def extract_features_task(self, track_id):
    try:
        track = Track.objects.get(id=track_id)
        file_path = track.audio_file.path

        if not os.path.exists(file_path):
            return

        features = extract_features(file_path)

        # Save or update track features + embedding
        track_feature, created = TrackFeature.objects.get_or_create(track=track)
        for key, value in features.items():
            setattr(track_feature, key, value)

        # ⏩ Call the embedding generator
        track_feature.embedding = track_feature.generate_embedding()

        track_feature.save()

    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def generate_recommendations_task():
    """
    Celery task to trigger full user recommendation regeneration.
    """
    try:
        subprocess.run(['python', 'manage.py', 'generate_recommendations'], check=True)
        return "Successfully regenerated all recommendations."
    except subprocess.CalledProcessError as e:
        return f"Error regenerating recommendations: {e}"
