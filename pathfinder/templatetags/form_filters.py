from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    else:
        # Отладочная информация
        raise ValueError("Ожидался объект поля формы, но был передан: {}".format(type(field)))

