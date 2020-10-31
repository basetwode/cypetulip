from django import forms
from django.utils.safestring import mark_safe


class SearchField(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs)
        inline_code = mark_safe(
            "<script>"
            '$("#id_search").on("keyup", function() {'
            'var value = $(this).val().toLowerCase();'
            '$(".searchable *").filter(function() {'
            '$(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)'
            '});'
            '});'
            "</script>"
        )
        return html + inline_code


class SearchableSelect(forms.Select):
    def render(self, name, value, attrs=None, renderer=None):
        attrs.pop('multiple', None)
        attrs.update({'class': 'searchable form-control'})
        attrs.update({'size': 10})
        return super(SearchableSelect, self).render(name, value, attrs, renderer)
