from django import template
from appSMS.permissions import has_permission 

register = template.Library()

@register.simple_tag
def has_perm(user, code):
    """
    Uso en template:
        {% has_perm user "restringir" as puede %}
        {% if puede %}
            <!-- Mostrar algo si tiene permiso -->
        {% endif %}
    """
    return has_permission(user, code)


@register.filter
def alias_prefix(value):
    """
    Devuelve solo la parte antes del guion bajo en un alias.
    Ej: 'Soporte_Pedro' → 'Soporte'
    """
    if value and "_" in value:
        return value.split("_")[0]
    return value
