from django.db import models
from django.conf import settings
from music.models import Track
from users.models import User

# Playlist Model
class Playlist(models.Model):
    PLAYLIST_TYPES = [
        ('most_liked',  'Most Liked'),
        ('admin_picks', 'Admin Picks'),
        ('for_you',     'For You'),
        ('liked_songs', 'Liked Songs'),
    ]
    
    name       = models.CharField(
        max_length=20,
        choices=PLAYLIST_TYPES,
        db_index=True                          # index for filtering by type
    )
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,
    blank=True,   
    db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True                          # index for ordering
    )

    class Meta:
        unique_together = ('name', 'user')
        ordering = ['-created_at']             # default ordering

    def __str__(self):
        return f"{self.get_name_display()} ({self.user.username})"


# Playlist Tracks Model
class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='playlist_tracks',
        db_index=True
    )
    track    = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='in_playlists',
        db_index=True
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        unique_together = ('playlist', 'track')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.playlist} → {self.track}"


# Recommendation Model
class Recommendation(models.Model):
    track    = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='recommendations',
        db_index=True
    )
    added_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"Recommended: {self.track.title}"


class UserRecommendation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendations')
    tracks = models.ManyToManyField(Track, related_name='recommended_to_users')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recommendations for {self.user.username}"