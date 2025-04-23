from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from playlists.models import Playlist, PlaylistTrack, Recommendation, UserRecommendation
from playlists.serializers import (
    PlaylistSerializer,
    PlaylistTrackSerializer,
    RecommendationSerializer,
    UserRecommendationSerializer,
)
from music.serializers import TrackSerializer

from django.db.models import Q

# ----------------------------
# Permissions
# ----------------------------
class IsPlaylistOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.playlist.user == request.user

# ----------------------------
# Playlist ViewSet
# ----------------------------
class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        public_playlists = Q(name__in=['most_liked', 'admin_picks'])

        if not user.is_authenticated:
            return Playlist.objects.filter(public_playlists)
        return Playlist.objects.filter(public_playlists | Q(user=user))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ----------------------------
# Playlist Track ViewSet
# ----------------------------
class PlaylistTrackViewSet(viewsets.ModelViewSet):
    queryset = PlaylistTrack.objects.all()
    serializer_class = PlaylistTrackSerializer
    permission_classes = [permissions.IsAuthenticated, IsPlaylistOwner]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        # short-circuit swagger’s fake inspection request
        if getattr(self, 'swagger_fake_view', False):
            return PlaylistTrack.objects.none()

        # real request: only your own playlist tracks
        return PlaylistTrack.objects.filter(playlist__user=self.request.user)

    def perform_create(self, serializer):
        playlist = serializer.validated_data['playlist']
        if playlist.user != self.request.user:
            raise PermissionDenied("You can only add tracks to your own playlists.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)
# ----------------------------
# Recommendation Admin ViewSet (for Admins and Moderators)
# ----------------------------
class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['track__title']

    def perform_create(self, serializer):
        if self.request.user.role not in ['admin', 'moderator']:
            raise PermissionDenied("Only admins or moderators can add recommendations.")
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role not in ['admin', 'moderator']:
            raise PermissionDenied("Only admins or moderators can modify recommendations.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role not in ['admin', 'moderator']:
            raise PermissionDenied("Only admins or moderators can remove recommendations.")
        instance.delete()

# ----------------------------
# Personalized User Recommendations View
# ----------------------------
class UserRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get personalized recommendations for the logged-in user")
    def get(self, request):
        user_recommendations = UserRecommendation.objects.filter(user=request.user).select_related('track').order_by('created_at')
        serializer = UserRecommendationSerializer(user_recommendations, many=True)
        return Response(serializer.data)

# ----------------------------
# 10 Tracks Recommendation (Simple View)
# ----------------------------
class RecommendedTracksView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get 10 recommended tracks for the user")
    def get(self, request):
        user_recommendations = UserRecommendation.objects.filter(user=request.user).select_related('track').order_by('created_at')[:10]
        tracks = [rec.track for rec in user_recommendations]
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)
