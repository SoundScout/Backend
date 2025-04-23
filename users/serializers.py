from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User, Follow, Artist
from .models import UserPreference
# ----------------------------
# Basic User Serializer
# ----------------------------
class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_profile_picture(self, obj):
        return obj.get_profile_picture() if obj.profile_picture else None


# ----------------------------
# Follow System
# ----------------------------
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


# ----------------------------
# Artist Profile (for admin/moderators/front)
# ----------------------------
class ArtistSerializer(serializers.ModelSerializer):
    user_email     = serializers.EmailField(source='user.email', read_only=True)
    username       = serializers.CharField(source='user.username', read_only=True)
    phone_number   = serializers.CharField(read_only=True)
    portfolio_link = serializers.URLField(read_only=True)

    class Meta:
        model = Artist
        fields = [
            'id',
            'user',
            'username',
            'user_email',
            'display_name',
            'bio',
            'profile_picture',
            'status',
            'created_at',
            'phone_number',    # ← newly added
            'portfolio_link',  # ← newly added
        ]
        read_only_fields = [
            'status',
            'created_at',
            'user_email',
            'username',
            'phone_number',    # ← mark read-only
            'portfolio_link',  # ← mark read-only
        ]
        ref_name = "UsersArtist"

# ----------------------------
# Listener Registration
# ----------------------------
class ListenerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.role = 'listener'
        user.save()
        return user


# ----------------------------
# Artist Registration (listener + artist profile = pending)
# ----------------------------
class ArtistRegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    portfolio_link = serializers.URLField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'profile_picture', 'phone_number', 'portfolio_link']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone = validated_data.pop('phone_number')
        portfolio = validated_data.pop('portfolio_link')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_picture=validated_data.get('profile_picture', ''),
            role='listener'  # will be upgraded upon approval
        )

        Artist.objects.create(
            user=user,
            display_name=user.username,
            phone_number=phone,
            portfolio_link=portfolio,
            profile_picture=user.profile_picture,
            status='pending'
        )

        return user


# ----------------------------
# Login Serializer
# ----------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return {'user': user}
        raise serializers.ValidationError("Invalid email or password")
    

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['favorite_genres', 'favorite_moods']


