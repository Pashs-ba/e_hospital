from django import template

register = template.Library()


@register.filter
def dict_get(item, d: dict):
    print(d[int(item)])
    return d[int(item)]


@register.filter
def subtract(value, arg):
    return value - arg
