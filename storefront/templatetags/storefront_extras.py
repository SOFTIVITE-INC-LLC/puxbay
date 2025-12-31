from django import template
import random

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Returns the value turned into a list.
    """
    return value.split(key)

@register.filter(name='random_choice')
def random_choice(value):
    """
    Returns a random item from the list.
    """
    try:
        return random.choice(value)
    except (TypeError, IndexError):
        return ''

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='divide')
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter(name='subtract')
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='subtract_percentage')
def subtract_percentage(value, percentage):
    try:
        val = float(value)
        perc = float(percentage)
        return val - (val * perc / 100)
    except (ValueError, TypeError):
        return value
