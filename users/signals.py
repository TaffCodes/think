# users/signals.py
#
# This file will automatically create a UserProfile when a new User is created

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile for new users, or just save the profile for existing users.
    """
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()