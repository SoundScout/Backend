from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from subscriptions.models import Subscription, SubscriptionPlan
from subscriptions.serializers import SubscriptionSerializer, SubscriptionPlanSerializer


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Artists can create, view, update, and delete their own subscription.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        # Only return the subscription belonging to this user’s artist profile
        user = self.request.user
        if hasattr(user, 'artist'):
            return Subscription.objects.filter(artist=user.artist)
        return Subscription.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        # Only artists (with an approved Artist profile) may create
        if not hasattr(user, 'artist'):
            raise PermissionDenied("Only approved artists can create subscriptions.")

        # Prevent creating more than one
        if Subscription.objects.filter(artist=user.artist).exists():
            raise PermissionDenied("You already have a subscription.")

        serializer.save(artist=user.artist)

    def perform_update(self, serializer):
        user = self.request.user
        subscription = self.get_object()

        # Only the owner (or admin/moderator) can update
        if subscription.artist.user != user and user.role not in ['admin', 'moderator']:
            raise PermissionDenied("You can only update your own subscription.")

        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        subscription = self.get_object()
        user = request.user

        # Only the owner (or admin/moderator) can delete
        if subscription.artist.user != user and user.role not in ['admin', 'moderator']:
            raise PermissionDenied("You can only delete your own subscription.")

        return super().destroy(request, *args, **kwargs)