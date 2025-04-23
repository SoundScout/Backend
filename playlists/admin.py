from django.contrib import admin
from .models import Playlist, PlaylistTrack, Recommendation

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display  = ['name', 'user', 'created_at']
    list_filter   = ['name', 'created_at']
    search_fields = ['user__username']
    ordering      = ['-created_at']

@admin.register(PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display  = ['playlist', 'track', 'added_at']
    list_filter   = ['playlist', 'added_at']
    search_fields = ['playlist__name', 'track__title']
    ordering      = ['-added_at']

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display  = ['track', 'added_at']
    list_filter   = ['added_at']
    search_fields = ['track__title']
    ordering      = ['-added_at']