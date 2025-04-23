# users/signals.py

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from users.models import User, UserPreference, Artist
from users.utils import assign_group
from subscriptions.models import Subscription, SubscriptionPlan

# 1) Keep your existing user/group sync and preference creation:

@receiver(post_save, sender=User)
def sync_user_group(sender, instance, **kwargs):
    """
    After any User.save(), ensure their group matches their role.
    """
    assign_group(instance)


@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        UserPreference.objects.create(user=instance)


# 2) New: capture old status before saving an existing Artist
@receiver(pre_save, sender=Artist)
def capture_artist_old_status(sender, instance, **kwargs):
    if not instance.pk:
        # brand-new Artist, no “old” status
        return
    try:
        old = sender.objects.get(pk=instance.pk)
        instance._old_status = old.status
    except sender.DoesNotExist:
        instance._old_status = None


# 3) After Artist.save(), react to any status change
@receiver(post_save, sender=Artist)
def sync_artist_status(sender, instance, created, **kwargs):
    """
    On status change:
      - If approved → promote User to 'artist', assign group, and grant free subscription.
      - If rejected  → (optional) demote or take other action.
    """
    # skip on first create
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    # only act when the status actually changed
    if old_status == new_status:
        return

    user = instance.user

    if new_status == 'approved':
        # promote user
        user.role = 'artist'
        user.save(update_fields=['role'])
        assign_group(user)

        # give free plan if they don't already have one
        free_plan = SubscriptionPlan.objects.filter(name='Free').first()
        if free_plan and not Subscription.objects.filter(artist=instance).exists():
            Subscription.objects.create(
                artist=instance,
                plan=free_plan,
                status='active'
            )

    elif new_status == 'rejected':
        # if you ever want to demote back to listener, uncomment:
        # user.role = 'listener'
        # user.save(update_fields=['role'])
        # assign_group(user)
        pass

