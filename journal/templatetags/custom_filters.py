from django import template

register = template.Library()

@register.filter
def make_chunks(value, chunk_size):
    return [value[i:i + chunk_size] for i in range(0, len(value), chunk_size)]

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])