# backend/backend/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

# Music Views
from music.views import (
    ArtistViewSet,
    TrackViewSet,
    TrackFeatureViewSet,
    InteractionViewSet,
    ListeningHistoryViewSet,
    TrackStatisticsViewSet,
    MyTracksView,
    TracksByArtistView,
)

# Playlist Views
from playlists.views import (
    PlaylistViewSet,
    PlaylistTrackViewSet,
    RecommendationViewSet,
    UserRecommendationView,
    RecommendedTracksView,
)

# Subscription Views
from subscriptions.views import (
    SubscriptionViewSet,
    SubscriptionPlanViewSet,
)

# -----------------------
# DRF Router Registration
# -----------------------
router = DefaultRouter()

# Music endpoints
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'tracks', TrackViewSet, basename='track')
router.register(r'track-features', TrackFeatureViewSet, basename='trackfeature')
router.register(r'interactions', InteractionViewSet, basename='interaction')
router.register(r'listening-history', ListeningHistoryViewSet, basename='listeninghistory')
router.register(r'track-statistics', TrackStatisticsViewSet, basename='trackstatistics')

# Playlist endpoints
router.register(r'playlists', PlaylistViewSet, basename='playlist')
router.register(r'playlist-tracks', PlaylistTrackViewSet, basename='playlisttrack')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

# Subscription endpoints
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscriptionplan')

# -----------------------
# Swagger Documentation
# -----------------------
schema_view = get_schema_view(
    openapi.Info(
        title="SoundScout API",
        default_version='v1',
        description="API documentation for SoundScout",
        terms_of_service="https://www.soundscout.com/terms/",
        contact=openapi.Contact(email="support@soundscout.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

# -----------------------
# URL Patterns
# -----------------------
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Core API (v1)
    path('api/v1/', include(router.urls)),

    # Users (login, registration, onboarding, moderation, follows)
    path('api/v1/users/', include('users.urls')),

    # Custom music views
    path('api/v1/my-tracks/', MyTracksView.as_view(), name='my-tracks'),
    path('api/v1/moderate/artist/<int:artist_id>/tracks/', TracksByArtistView.as_view(), name='artist-tracks-moderator'),

    # User personalized recommendations
    path('api/v1/user-recommendations/', UserRecommendationView.as_view(), name='user-recommendations'),
    path('api/v1/recommended-tracks/', RecommendedTracksView.as_view(), name='recommended-tracks'),

    # Swagger & Redoc
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger\.json$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# ✅ Serve Media Files (audio, images, etc.)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
