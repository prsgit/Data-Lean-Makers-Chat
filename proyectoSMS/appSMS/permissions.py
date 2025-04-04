from .models import RolePermission
from django.contrib.auth import get_user_model



User = get_user_model()



def has_permission(user, code):
    """
    función para saber si el usuario tiene activado un permiso (allowed=True) para su rol.
    
    :param user: instancia del usuario (User)
    :param code: string del código del permiso (por ejemplo, "Restringir")
    :return: True si el permiso está activado, False si no lo tiene o está en False
    """
    # Obtener todos los roles asignados al usuario (puede tener varios)
    assignments = user.assigned_roles.select_related('role') # select_related hace un join de UserRoleAssignment y UserSystemRole

    for assignment in assignments:
        # Buscar si este rol tiene asignado el permiso
        try:
            permission = RolePermission.objects.get(
                role=assignment.role,
                permission_type__code=code # trae los RolePermission cuyo permission_type.code sea "...."
            )
            if permission.allowed:
                return True  # Si al menos uno de los roles asignados a ese usuario esta activado, retornamos True
        except RolePermission.DoesNotExist:
            continue  # Este rol no tiene ese permiso, seguimos con el siguiente

    return False  # Ningún rol tiene el permiso activado



def get_anonymous_role(user):
    """
    Busca entre todos los roles asignados a un usuario y devuelve el primero que tenga
    activado el permiso 'anonimo'. Este rol será usado para mostrar el alias del usuario
    en lugar de su nombre real (por ejemplo, 'Soporte').
    Devuelve el primer rol del usuario que tenga activado el permiso 'anonimo'.
    Si no tiene ninguno, devuelve None.
    """
    # Obtener todas las asignaciones de rol del usuario, cargando también el rol con select_related
    assignments = user.assigned_roles.select_related("role")

    # Recorremos cada asignación para verificar si el rol tiene el permiso 'anonimo' activado
    for assignment in assignments:
        role = assignment.role
        try:
            # Buscamos si el rol tiene el permiso 'anonimo' configurado
            permission = RolePermission.objects.get(
                role=role,
                permission_type__code="anonimo"
            )
            if permission.allowed:
                return role  # Devolvemos el rol si tiene el permiso activado
        except RolePermission.DoesNotExist:
            continue  # Si el permiso no está configurado en ese rol, seguimos al siguiente

    return None  # Si ningún rol tiene el permiso 'anonimo', devolvemos None



def get_visible_contacts(user):
    """
    Devuelve una lista de contactos visibles para el usuario.
    Si tiene el permiso 'contactos' activado, solo verá los contactos asignados.
    Si no, verá a todos los demás usuarios excepto al admin.
    """
    if has_permission(user, "contactos"):
        contact_list = getattr(user, 'restricted_contacts', None)
        if contact_list:
            return contact_list.allowed_users.all()
        return User.objects.none()
    else:
        return User.objects.exclude(username='admin')