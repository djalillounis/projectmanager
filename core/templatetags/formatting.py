from django import template
from datetime import datetime

register = template.Library()

@register.filter
def format_iso(value):
    """
    Converts an ISO datetime string to 'dd-mm-yyyy hh:mm' format.
    """
    try:
        # Remove 'Z' if present (e.g., "2025-03-25T10:05:30Z")
        if isinstance(value, str) and value.endswith('Z'):
            value = value[:-1]
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return value
