from django import template
from appSMS.permissions import has_group_permission, has_permission 

register = template.Library()


@register.simple_tag(takes_context=True)
def has_perm(context, user, code):
    """
    Template tag unificado para permisos globales o de grupo.

    - Si `selected_group` está en el contexto, verifica permisos dentro del grupo.
    - Si no está en un grupo, verifica permisos globales.
    """
    group = context.get('selected_group')  # se usa automáticamente si existe
    if group:
        return has_group_permission(user, group, code)
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
