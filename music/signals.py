from django.db.models.signals import post_save
from django.dispatch import receiver
from music.models import Track
from music.tasks import extract_features_task

@receiver(post_save, sender=Track)
def enqueue_feature_extraction(sender, instance, created, **kwargs):
    """
    When a Track is approved and has no features yet, enqueue a Celery task
    to extract features asynchronously.
    """
    if instance.approval_status == 'approved':
        # Only enqueue if no TrackFeature exists
        if not hasattr(instance, 'trackfeature'):
            # Ensure there's a local file to process
            try:
                file_path = instance.audio_file.path
            except Exception:
                return

            # Enqueue the background task
            extract_features_task.delay(instance.id)