from django import template
register = template.Library()

@register.filter
def get_item(dataframe, key):
    return dataframe[key]