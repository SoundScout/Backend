from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
    Group, Permission
)


# ------------------------------
# Custom User Manager
# ------------------------------
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


# ------------------------------
# Custom User Model
# ------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('listener', 'Listener'),
        ('artist', 'Artist'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='listener')
    preferences_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def get_profile_picture(self):
        if self.profile_picture:
            return self.profile_picture
        return "https://your-default-avatar-url.com/default.png"
    
    def is_artist(self):
        return self.role == 'artist'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# ------------------------------
# Artist Profile (For Approved Artists)
# ------------------------------
class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    profile_picture = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)    # ✅ ADD
    portfolio_link = models.URLField(max_length=255, blank=True, null=True)  # ✅ ADD

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('denied', 'Denied')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username

    class Meta:
        permissions = [
            ("approve_artist", "Can approve artist"),
            ("reject_artist", "Can reject artist"),
            ("deactivate_artist", "Can deactivate artist to listener"),
        ]


# ------------------------------
# Follow Relationship (User to User)
# ------------------------------
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    def save(self, *args, **kwargs):
        if self.follower == self.following:
            raise ValueError("Users cannot follow themselves.")
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('follower', 'following')

        # users/models.py

from django.db import models
from django.conf import settings

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preference')

    favorite_genres = models.JSONField(default=list)  # Example: ["Pop", "Hip-Hop"]
    favorite_moods = models.JSONField(default=list)   # Example: ["Happy", "Energetic"]

    average_tempo = models.FloatField(null=True, blank=True)
    average_danceability = models.FloatField(null=True, blank=True)
    average_energy = models.FloatField(null=True, blank=True)
    average_valence = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences of {self.user.email}"
    