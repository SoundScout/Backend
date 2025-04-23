from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from music.models import Track
from users.models import Artist  # adjust if needed

def create_roles():
    # Listener
    listener_group, _ = Group.objects.get_or_create(name="listener")

    # Artist
    artist_group, _ = Group.objects.get_or_create(name="artist")
    # Example: Can add track
    artist_permissions = Permission.objects.filter(codename__in=[
        "add_track", "change_track", "delete_track", "view_track"
    ])
    artist_group.permissions.set(artist_permissions)

    # Moderator
    moderator_group, _ = Group.objects.get_or_create(name="moderator")
    # Example: Can change approval status of tracks
    moderator_permissions = Permission.objects.filter(codename__in=[
        "change_track", "view_track", "delete_track"
    ])
    moderator_group.permissions.set(moderator_permissions)

    # Admin
    admin_group, _ = Group.objects.get_or_create(name="admin")
    # Give them everything
    all_permissions = Permission.objects.all()
    admin_group.permissions.set(all_permissions)

    print("✅ Roles and permissions created!")