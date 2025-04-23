# playlists/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from playlists.views import (
    PlaylistViewSet,
    PlaylistTrackViewSet,
    RecommendationViewSet,
    UserRecommendationView,
    RecommendedTracksView,
)

# ----------------------------
# Router Setup
# ----------------------------
router = DefaultRouter()
router.register(r'playlists', PlaylistViewSet, basename='playlist')
router.register(r'playlist-tracks', PlaylistTrackViewSet, basename='playlisttrack')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

# ----------------------------
# URL Patterns
# ----------------------------
urlpatterns = [
    path('user-recommendations/', UserRecommendationView.as_view(), name='user-recommendations'),
    path('recommended-tracks/', RecommendedTracksView.as_view(), name='recommended-tracks'),
]

urlpatterns += router.urls
