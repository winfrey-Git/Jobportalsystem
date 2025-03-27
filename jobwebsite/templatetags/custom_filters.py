from django import template

register = template.Library()

@register.filter
def dictfilter(queryset, status):
    """Filters a list of dictionaries by the 'status' key."""
    if isinstance(queryset, list):
        return [item for item in queryset if item.get("status") == status]
    return queryset
