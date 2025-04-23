# music/admin.py
from music.tasks import extract_features_task
from django.contrib import admin
from .models import Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics
from celery import shared_task
import subprocess

# ✅ Track Admin
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'approval_status', 'created_at']
    list_filter = ['approval_status', 'genre', 'created_at']
    search_fields = ['title', 'artist__display_name']
    ordering = ['-created_at']
    exclude = ['created_at']
    readonly_fields = ['duration']

    fieldsets = (
        (None, {
            'fields': ('artist', 'title', 'genre', 'lyrics')
        }),
        ('Audio and Artwork', {
            'fields': ('audio_file', 'artwork_file', 'demo_start_time', 'duration')
        }),
        ('Approval', {
            'fields': ('approval_status', 'rejection_reason')
        }),
    )

    def save_model(self, request, obj, form, change):
        # ✅ Check if status changed to APPROVED
        is_new_approval = change and 'approval_status' in form.changed_data and obj.approval_status == 'approved'
        
        super().save_model(request, obj, form, change)

        if is_new_approval:
            # ✅ Launch feature extraction if approved!
            extract_features_task.delay(obj.id)

# ✅ Track Feature Admin
@admin.register(TrackFeature)
class TrackFeatureAdmin(admin.ModelAdmin):
    list_display = ['track', 'danceability', 'energy', 'valence', 'mood']
    list_filter = ['mood']
    search_fields = ['track__title']
    ordering = ['track']

# ✅ Interaction Admin
@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'track', 'interaction_type', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'track__title']
    ordering = ['-created_at']

# ✅ Listening History Admin
@admin.register(ListeningHistory)
class ListeningHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'track', 'listened_at']
    list_filter = ['listened_at']
    search_fields = ['user__username', 'track__title']
    ordering = ['-listened_at']

# ✅ Track Statistics Admin
@admin.register(TrackStatistics)
class TrackStatisticsAdmin(admin.ModelAdmin):
    list_display = ['track', 'plays_count', 'likes_count', 'comments_count', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['track__title']
    ordering = ['-updated_at']

# ✅ Celery Task for Regenerating Recommendations
@shared_task
def regenerate_recommendations_task():
    """Call the management command to regenerate all user recommendations."""
    try:
        subprocess.run(["python", "manage.py", "generate_recommendations"], check=True)
        return "Successfully regenerated recommendations."
    except subprocess.CalledProcessError as e:
        return f"Error regenerating recommendations: {e}"
