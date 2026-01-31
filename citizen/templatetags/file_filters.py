from django import template

register = template.Library()

@register.filter
def endswith(value, suffix):
    """Check if the string ends with the given suffix."""
    if not value:
        return False
    return str(value).lower().endswith(suffix.lower())

