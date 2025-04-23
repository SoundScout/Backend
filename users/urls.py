# users/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter



from users.views import (
    ListenerRegisterView,
    ArtistRegisterView,
    LoginView,
    #   ApproveOrRejectArtistView,
    ArtistViewSet,
    UserViewSet,
    FollowViewSet,
    LogoutView,
    OnboardingPreferenceView,
    ClearPreferenceView,
    PendingArtistListView,
    PendingArtistCountView,
    ApproveArtistView,
    RejectArtistView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'follows', FollowViewSet)
router.register(r'artists', ArtistViewSet, basename='artist-profiles')

urlpatterns = [
    path('register/listener/', ListenerRegisterView.as_view(), name='register-listener'),
    path('register/artist/', ArtistRegisterView.as_view(), name='register-artist'),
    path('login/', LoginView.as_view(), name='login'),
# path('moderate/artist/<int:artist_id>/', ApproveOrRejectArtistView.as_view(), name='moderate-artist'),
    path('logout/', LogoutView, name='logout'),
    path('onboarding/preferences/', OnboardingPreferenceView.as_view(), name='onboarding-preferences'),
    path('onboarding/clear-preferences/', ClearPreferenceView.as_view(), name='clear-preferences'),
    path('artists/pending/', PendingArtistListView.as_view(), name='pending-artists'),
    path('artists/pending/count/', PendingArtistCountView.as_view(), name='pending-artists-count'),
    path('artists/<int:artist_id>/approve/',
           ApproveArtistView.as_view(),
           name='artist-approve'),
    path('artists/<int:artist_id>/reject/',
           RejectArtistView.as_view(),
           name='artist-reject'),
]

urlpatterns += router.urls
