from django.template.defaulttags import register
import os

@register.filter
def basename(value):
    return os.path.basename(value.name)