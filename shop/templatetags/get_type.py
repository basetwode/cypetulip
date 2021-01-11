__author__ = 'Anselm'

from django import template

register = template.Library()


@register.filter
def get_var(dictionary, key):
    return dictionary.get(key) if dictionary else None


@register.filter
def is_available(button, arg):
    return button['is_available'](arg)


@register.filter(name='addcss')
def addcss(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter(name='countchars')
def count_chars(value, char):
    return value.count(char)