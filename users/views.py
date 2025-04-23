import logging
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, Follow, Artist, UserPreference
from users.serializers import (
    UserSerializer,
    FollowSerializer,
    ArtistSerializer,
    ListenerRegisterSerializer,
    ArtistRegisterSerializer,
    LoginSerializer,
    UserPreferenceSerializer,
)
from subscriptions.models import Subscription, SubscriptionPlan
from users.utils import assign_group

logger = logging.getLogger('users')


# ----------------------------
# User CRUD (Used by admin / profile screen)
# ----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Follow/Unfollow Users
# ----------------------------
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Listener Registration
# ----------------------------
class ListenerRegisterView(generics.CreateAPIView):
    serializer_class = ListenerRegisterSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role if hasattr(user, 'role') else "listener"
            }
        }, status=status.HTTP_201_CREATED)


# ----------------------------
# Artist Registration (listener role + artist profile = pending)
# ----------------------------
class ArtistRegisterView(generics.CreateAPIView):
    serializer_class = ArtistRegisterSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Login View for All Users
# ----------------------------
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "user_id": user.id,
            "email": user.email,
            "username": user.username,     
            "preferences_completed": user.preferences_completed,
        })


# ----------------------------
# View All Artists (moderator/admin only)
# ----------------------------
class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Approve or Reject Artist (moderator/admin only)
# ----------------------------
# class ApproveOrRejectArtistView(APIView):
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend]

#     def post(self, request, artist_id):
#         # Only moderators or admins
#         if request.user.role not in ('moderator', 'admin'):
#             raise PermissionDenied("Only moderators or admins can perform this action.")

#         artist = get_object_or_404(Artist, id=artist_id)
#         action = request.data.get('action', '').lower()
#         rejection_reason = request.data.get('rejection_reason', '').strip()

#         if action == 'approve':
#             with transaction.atomic():
#                 # 1) Update Artist
#                 artist.status = 'approved'
#                 artist.rejection_reason = ''
#                 artist.save(update_fields=['status', 'rejection_reason'])

#                 # 2) Promote User
#                 user = artist.user
#                 user.role = 'artist'
#                 user.save(update_fields=['role'])
#                 assign_group(user)

#                 # 3) Grant Free Subscription if not already present
#                 free_plan = SubscriptionPlan.objects.filter(name='Free').first()
#                 if free_plan and not Subscription.objects.filter(artist=artist).exists():
#                     Subscription.objects.create(
#                         artist=artist,
#                         plan=free_plan,
#                         status='active'
#                     )
#                     logger.info(f"🆕 Free subscription created for artist '{artist.display_name}'")
#                 else:
#                     logger.warning(f"⚠️ Free subscription skipped for '{artist.display_name}'")

#             return Response(
#                 {"message": "Artist approved, user promoted to 'artist', and free subscription granted."},
#                 status=status.HTTP_200_OK
#             )

#         elif action == 'reject':
#             if not rejection_reason:
#                 return Response(
#                     {"error": "Rejection reason is required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             artist.status = 'rejected'
#             artist.rejection_reason = rejection_reason
#             artist.save(update_fields=['status', 'rejection_reason'])

#             logger.info(
#                 f"Artist '{artist.display_name}' (User: {artist.user.email}) "
#                 f"rejected by {request.user.email}. Reason: {rejection_reason}"
#             )
#             return Response({"message": "Artist rejected."}, status=status.HTTP_200_OK)

#         else:
#             return Response(
#                 {"error": "Invalid action. Use 'approve' or 'reject'."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
class ApproveArtistView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def post(self, request, artist_id):
        if request.user.role not in ('moderator', 'admin'):
            raise PermissionDenied("Only moderators or admins can perform this action.")

        artist = get_object_or_404(Artist, id=artist_id)

        with transaction.atomic():
            # — 1) mark artist approved —
            artist.status           = 'approved'
            artist.save(update_fields=['status'])

            # — 2) promote user to artist —
            user = artist.user
            user.role = 'artist'
            user.save(update_fields=['role'])
            assign_group(user)

            # — 3) safely grant free subscription —
            free_plan = SubscriptionPlan.objects.filter(name='Free').first()
            if free_plan and not Subscription.objects.filter(artist=artist).exists():
                try:
                    Subscription.objects.create(
                        artist=artist,
                        plan=free_plan,
                        status='active',
                        end_subscription=timezone.now() + relativedelta(months=1)
                    )
                    logger.info(f"🆕 Free subscription created for '{artist.display_name}'")
                except Exception as exc:
                    # swallow the error so we don’t return 500
                    logger.error(f"Failed to create subscription: {exc}")

        return Response(
            {"message": "Artist approved, user promoted, and free subscription granted (if possible)."},
            status=status.HTTP_200_OK
        )

class RejectArtistView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]
    filter_backends        = [DjangoFilterBackend]

    def post(self, request, artist_id):
        if request.user.role not in ('moderator', 'admin'):
            raise PermissionDenied("Only moderators or admins can perform this action.")

        artist = get_object_or_404(Artist, id=artist_id)

        artist.status           = 'rejected'
        artist.save(update_fields=['status'])

        user = artist.user
        user.role = 'listener'
        user.save(update_fields=['role'])
        assign_group(user)

        logger.info(
            f"Artist '{artist.display_name}' (User: {artist.user.email}) "
        )
        return Response({"message": "Artist rejected."}, status=status.HTTP_200_OK)

# ----------------------------
# Logout View
# ----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def LogoutView(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OnboardingPreferenceView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserPreferenceSerializer
    filter_backends = [DjangoFilterBackend]

    def post(self, request):
        # 1) ensure preference row exists
        preference, _ = UserPreference.objects.get_or_create(user=request.user)

        # 2) validate & save
        serializer = self.get_serializer(preference, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        # 3) mark completion flag
        request.user.preferences_completed = True
        request.user.save(update_fields=['preferences_completed'])

        return Response(
            {"message": "Preferences saved successfully!"},
            status=status.HTTP_200_OK
        )
# ----------------------------
# Clear User Preferences (Reset preference and set preferences_completed=False)
# ----------------------------
class ClearPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        preference = request.user.preference
        preference.favorite_genres.clear()
        preference.favorite_moods.clear()
        preference.save()

        request.user.preferences_completed = False
        request.user.save(update_fields=['preferences_completed'])

        return Response({"message": "Preferences cleared successfully."}, status=status.HTTP_200_OK)
    
class PendingArtistListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ArtistSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role not in ('moderator', 'admin'):
            raise PermissionDenied("Only moderators and admins can view pending artists.")
        return Artist.objects.filter(status='pending')
    
class PendingArtistCountView(APIView):
    """
    GET /api/v1/users/artists/pending/count/
    Returns {"count": <number of pending artists>}.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ('moderator', 'admin'):
            raise PermissionDenied("Only moderators/admins.")
        count = Artist.objects.filter(status='pending').count()
        return Response({'count': count}, status=status.HTTP_200_OK)