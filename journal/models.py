from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from datetime import timedelta

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # Code is valid for 10 minutes
        return not self.is_used and timezone.now() < self.created_at + timedelta(minutes=10)

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class BulletJournalKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    description = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#000000')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.symbol} - {self.description}"


class Log(models.Model):
    TYPE_CHOICES = [
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
        ('unplanned', 'Unplanned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    key = models.ForeignKey(BulletJournalKey, null=True, blank=True, on_delete=models.SET_NULL)
    log_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='unplanned')
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    week = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_log_type_display()})"

    def save(self, *args, **kwargs):
        # Automatically set log_type based on provided dates
        if self.year and not self.month and not self.week and not self.day:
            self.log_type = 'yearly'
        elif self.year and self.month and not self.week and not self.day:
            self.log_type = 'monthly'
        elif self.year and not self.month and self.week and not self.day:
            self.log_type = 'weekly'
        elif self.year and self.month and self.day:
            self.log_type = 'daily'
        else:
            self.log_type = 'unplanned'
        super().save(*args, **kwargs)