from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Returns the value for the given key from a dictionary.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)