from django import template
from datetime import datetime

register = template.Library()

@register.filter
def format_iso(value):
    """
    Converts an ISO datetime string or a datetime object to the format:
    'dd-MMM-YYYY HH:MM', e.g., '24-Mar-2025 10:32'
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
        return dt.strftime("%d-%b-%Y %H:%M")
    except Exception:
        return value