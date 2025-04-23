# music/models.py

from django.db import models
from users.models import Artist
from django.conf import settings

# 🆕 Mood Mapping
MOOD_MAPPING = {
    'happy': 1,
    'sad': 2,
    'energetic': 3,
    'calm': 4,
    'romantic': 5,
    'angry': 6,
    'chill': 7,
}

# ------------------------------
# Track Model
# ------------------------------
class Track(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="tracks")
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=50, blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)  # Duration in seconds
    demo_start_time = models.FloatField(default=0)

    audio_file = models.FileField(upload_to='audio_files/', blank=True, null=True)  # MP3 or WAV upload
    artwork_file = models.ImageField(upload_to='artwork_files/', blank=True, null=True)  # Artwork image

    spotify_link = models.URLField(blank=True, null=True)
    anghami_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    
    lyrics = models.TextField(blank=True, null=True)
    approval_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.artist.display_name}"

# ------------------------------
# Track Feature Model
# ------------------------------
class TrackFeature(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('energetic', 'Energetic'),
        ('calm', 'Calm'),
        ('romantic', 'Romantic'),
        ('angry', 'Angry'),
        ('chill', 'Chill'),
    ]

    track = models.OneToOneField(Track, on_delete=models.CASCADE)
    danceability = models.FloatField()
    energy = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    speechiness = models.FloatField()
    instrumentalness = models.FloatField()
    acousticness = models.FloatField()
    liveness = models.FloatField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, db_index=True)

    embedding = models.JSONField(blank=True, null=True)  # ✅ New Field

    class Meta:
        ordering = ['track']

    def save(self, *args, **kwargs):
        self.embedding = self.generate_embedding()
        super().save(*args, **kwargs)

    def generate_embedding(self):
        """
        Creates a numerical vector representing this track's features.
        """
        mood_numeric = MOOD_MAPPING.get(self.mood.lower(), 0)
        return [
            float(self.danceability),
            float(self.energy),
            float(self.valence),
            float(self.tempo),
            float(self.speechiness),
            float(self.instrumentalness),
            float(self.acousticness),
            float(self.liveness),
            float(mood_numeric),
        ]

# ------------------------------
# Interaction Model
# ------------------------------
class Interaction(models.Model):
    INTERACTION_TYPES = [
        ('like', 'Like'),
        ('stream', 'Stream'),
        ('comment', 'Comment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(
        max_length=10,
        choices=INTERACTION_TYPES,
        default='stream',
        db_index=True
    )
    comment_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.interaction_type == 'comment' and not self.comment_text:
            raise ValueError("Comment text is required when interaction_type is 'comment'.")
        if self.interaction_type != 'comment':
            self.comment_text = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.interaction_type} - {self.track}"

# ------------------------------
# Listening History Model
# ------------------------------
class ListeningHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    listened_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-listened_at']

# ------------------------------
# Track Statistics Model
# ------------------------------
class TrackStatistics(models.Model):
    track = models.OneToOneField(Track, on_delete=models.CASCADE)
    plays_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']
