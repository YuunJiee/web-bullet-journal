from django import template
from datetime import datetime
from django.utils import timezone

register = template.Library()

@register.simple_tag
def current_date_url(pattern):
    current_date = timezone.localdate()
    # strftime supports %G (ISO year) and %V (ISO week)
    return current_date.strftime(pattern)
