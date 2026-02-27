from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import BulletJournalKey

@receiver(post_save, sender=User)
def create_default_keys(sender, instance, created, **kwargs):
    if created:
        initial_keys = [
            {"user": instance, "symbol": "dot", "description": "Task", "color": "#5D5D5D", "is_default": True},
            {"user": instance, "symbol": "check-lg", "description": "Completed Task", "color": "#8BA888", "is_default": True},
            {"user": instance, "symbol": "chevron-right", "description": "Migrated Task", "color": "#D69A70", "is_default": True},
            {"user": instance, "symbol": "chevron-left", "description": "Scheduled Task", "color": "#829399", "is_default": True},
            {"user": instance, "symbol": "circle", "description": "Event", "color": "#C27F7C", "is_default": True},
            {"user": instance, "symbol": "dash-lg", "description": "Note", "color": "#A39A92", "is_default": True},
        ]
        for key in initial_keys:
            BulletJournalKey.objects.create(**key)
