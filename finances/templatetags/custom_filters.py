from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def percentage(value, arg):
    if arg == 0:
        return 0
    return (value / arg) * 100

@register.filter
def filter_by_type(categories, category_type):
    """Filter categories by type (income or expense)."""
    return categories.filter(type=category_type)