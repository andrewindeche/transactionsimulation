"""
Django signals for handling user-related events, such as creating 
accounts when a new user is created.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import NotFound
from .models import User, Account

@receiver(post_save, sender=User)
def create_account_for_new_user(instance, created):
    """
    Signal to create an account when a new user is created.
    """
    try:
        if created:
            Account.objects.create(user=instance)
            print(f"Account created for user: {instance.username}")
    except AttributeError as exc:
        raise NotFound("Account not found.") from exc
