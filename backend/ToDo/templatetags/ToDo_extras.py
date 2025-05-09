from django import template
from django.utils import timezone as tz

register = template.Library()


@register.filter(name='date_format')
def date_format(value: tz.datetime) -> str:
    """Format a date to a more readable format."""
    if value is None:
        return ''

    interval = value - tz.now()
    if interval.days == 0:
        return value.strftime("Today, %H:%M")
    elif interval.days == 1:
        return value.strftime("Tomorrow, %H:%M")
    elif interval.days == -1:
        return value.strftime("Yesterday, %H:%M")
    elif abs(interval.days/365) < 1:
        return value.strftime("%a, %b %d, %H:%M")
    return value.strftime("%a, %b %d, %Y, %H:%M")
