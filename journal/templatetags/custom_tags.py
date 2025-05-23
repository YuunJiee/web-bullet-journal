from django import template
from datetime import datetime

register = template.Library()

@register.simple_tag
def current_date_url(pattern):
    current_date = datetime.now()
    iso_year, iso_week, iso_day = current_date.isocalendar()
    
    formatted_date = current_date.strftime(
        pattern.replace('%Uw', f'{iso_week:02d}w')
               .replace('%Yy', f'{iso_year}y')
               .replace('%dd', f'{current_date.day:02d}d')
               .replace('%mm', f'{current_date.month:02d}m')
    )
    return formatted_date
