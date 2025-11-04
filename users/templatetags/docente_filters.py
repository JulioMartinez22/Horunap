from django import template

register = template.Library()

@register.filter
def filter_tipo(queryset, tipo):
    """Filtra un queryset por el campo tipo"""
    return queryset.filter(tipo=tipo)