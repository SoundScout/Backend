from rest_framework import serializers
from music.serializers import TrackSerializer
from music.models import Track
from .models import Playlist, PlaylistTrack, Recommendation, UserRecommendation

# ----------------------------
# Playlist Serializer
# ----------------------------
class PlaylistSerializer(serializers.ModelSerializer):
    track_count = serializers.SerializerMethodField()
    display_name = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'display_name', 'user', 'created_at', 'track_count']
        read_only_fields = ['user', 'created_at']

    def get_track_count(self, obj):
        return obj.playlist_tracks.count()

# ----------------------------
# PlaylistTrack Serializer
# ----------------------------
class PlaylistTrackSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)

    class Meta:
        model = PlaylistTrack
        fields = ['id', 'playlist', 'track', 'added_at']
        read_only_fields = ['added_at']

    def validate(self, data):
        request = self.context.get('request')
        playlist = data.get('playlist')
        track = data.get('track')

        if playlist.user != request.user:
            raise serializers.ValidationError("You can only add tracks to your own playlists.")

        if PlaylistTrack.objects.filter(playlist=playlist, track=track).exists():
            raise serializers.ValidationError("This track is already in the playlist.")

        return data

# ----------------------------
# Recommendation Serializer
# ----------------------------
class RecommendationSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = ['track']  # ✅ Only showing the track

# ----------------------------
# Track Basic Serializer
# ----------------------------
class TrackBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'title', 'artist', 'artwork_file', 'audio_file']

# ----------------------------
# User Recommendation Serializer (✅ FINAL FORM)
# ----------------------------
class UserRecommendationSerializer(serializers.ModelSerializer):
    track = TrackBasicSerializer(read_only=True)

    class Meta:
        model = UserRecommendation
        fields = ['user', 'track', 'score', 'created_at']
        read_only_fields = ['user', 'created_at']
