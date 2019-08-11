__author__ = 'Anselm'

from django import template

register = template.Library()


@register.filter
def get_var(dictionary, key):
    return dictionary.get(key)


@register.filter(name='addcss')
def addcss(value, arg):
    return value.as_widget(attrs={'class': arg})