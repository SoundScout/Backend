# music/management/commands/save_recommendations.py

from django.core.management.base import BaseCommand
from music.models import Track
from playlists.models import UserRecommendation
from users.models import User
from music.utils.recommendation_engine import generate_user_recommendations

class Command(BaseCommand):
    help = 'Save personalized recommendations for all users.'

    def handle(self, *args, **kwargs):
        users = User.objects.all()

        for user in users:
            recommended_tracks = generate_user_recommendations(user.id, top_n=10)

            # Clear existing recommendations first
            UserRecommendation.objects.filter(user=user).delete()

            # Create new recommendations
            for idx, track in enumerate(recommended_tracks):
                UserRecommendation.objects.create(
                    user=user,
                    track=track,
                    rank=idx + 1,
                )

            self.stdout.write(self.style.SUCCESS(f"Recommendations saved for user {user.username}"))
