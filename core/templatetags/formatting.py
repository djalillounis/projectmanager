from django import template
from datetime import datetime

register = template.Library()

@register.filter
def format_iso(value):
    """
    Converts an ISO datetime string or a datetime object to the format:
    'dd-MMM-yy HHHi', e.g., '01-Jan-25 13H00'
    """
    try:
        if isinstance(value, str):
            if value.endswith('Z'):
                value = value[:-1]
            dt = datetime.fromisoformat(value)
        elif isinstance(value, datetime):
            dt = value
        else:
            return value
        return dt.strftime("%d-%b-%y %H\\H%M")
    except Exception:
        return value
