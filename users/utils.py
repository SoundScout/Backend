# users/utils.py

from django.contrib.auth.models import Group

def assign_group(user):
    """
    Ensure the user is in exactly one group matching user.role.
    Clears any existing custom_user_groups first.
    """
    # Remove from all custom_user_groups
    user.groups.clear()

    # Try to add the group named after user.role
    try:
        group = Group.objects.get(name=user.role)
        user.groups.add(group)
    except Group.DoesNotExist:
        # If you expect the group might be missing, you could create it:
        # group = Group.objects.create(name=user.role)
        # user.groups.add(group)
        pass