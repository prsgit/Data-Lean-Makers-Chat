from .models import RolePermission, GroupMemberRole, GroupRolePermission, PermissionType
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




def has_group_permission(user, group, code):
    """
    Verifica si un usuario tiene un permiso específico activado dentro de un grupo.

    :param user: instancia del usuario
    :param group: instancia del grupo
    :param code: código del permiso (ej: "leer", "escribir")
    :return: True si el permiso está activado (allowed=True), False en caso contrario
    """
    try:
        # busca el rol del usuario en ese grupo
        member_role = GroupMemberRole.objects.get(user=user, group=group)

        # obtiene el permiso de un rol en ese grupo
        permission = GroupRolePermission.objects.get(
            group=group,
            role=member_role.role,
            permission_type__code=code
        )

        return permission.allowed  # muestra True si está permitido (allowed=True)

    except (GroupMemberRole.DoesNotExist, GroupRolePermission.DoesNotExist):
        return False  # si no tiene rol o no tiene permiso, se niega el acceso



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



def get_anonymous_group_role(user, group):
    """
    Busca el rol que tiene un usuario dentro de un grupo y verifica si tiene
    activado el permiso 'anonimo' en ese contexto grupal.
    
    :param user: Usuario que envía el mensaje.
    :param group: Grupo donde se evalúa.
    :return: Rol del usuario si tiene el permiso activado, o None si no.
    """
    try:
        # busca el rol que el usuario tiene en ese grupo
        member_role = GroupMemberRole.objects.get(user=user, group=group)
        role = member_role.role

        # busca si ese rol en ese grupo tiene activado el permiso 'anonimo'
        permission = GroupRolePermission.objects.get(
            group=group,
            role=role,
            permission_type__code="anonimo"
        )

        if permission.allowed:
            return role

    except (GroupMemberRole.DoesNotExist, GroupRolePermission.DoesNotExist):
        pass  # si no tiene rol o ese rol no tiene permiso anonimo se ignora y sigue

    return None # si no encontró nada, devuelve None



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



