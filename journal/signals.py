from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import BulletJournalKey

@receiver(post_save, sender=User)
def create_default_keys(sender, instance, created, **kwargs):
    if created:
        initial_keys = [
            {"user": instance, "symbol": "•", "description": "Task", "color": "#000000", "is_default": True},
            {"user": instance, "symbol": "x", "description": "Completed Task", "color": "#00FF00", "is_default": True},
            {"user": instance, "symbol": ">", "description": "Migrated Task", "color": "#FFA500", "is_default": True},
            {"user": instance, "symbol": "<", "description": "Scheduled Task", "color": "#0000FF", "is_default": True},
            {"user": instance, "symbol": "o", "description": "Event", "color": "#FF0000", "is_default": True},
            {"user": instance, "symbol": "-", "description": "Note", "color": "#A9A9A9", "is_default": True},
        ]
        for key in initial_keys:
            BulletJournalKey.objects.create(**key)
