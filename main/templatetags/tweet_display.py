from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter()
def tweet_display(text):
    result = re.sub('@mention', '<i>@mention</i>', text)
    result = re.sub('\[url\]', '<i>[url]</i>', result)
    return mark_safe(result)
