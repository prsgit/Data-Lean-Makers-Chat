from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, AllowedContacts, UserSystemRole, PermissionType, RolePermission

User = get_user_model()

# señal cuando creamos un perfil nuevo se agrega automáticamente el UserProfile de models.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente para un usuario nuevo.
    """
    if created:  # Solo ejecuta esto al crear un usuario nuevo
        UserProfile.objects.create(user=instance)
        print(f"Perfil creado para el usuario: {instance.username}")



# señal para mantener sincronizados los contactos de forma bidireccional
@receiver(m2m_changed, sender=AllowedContacts.allowed_users.through)
def sync_contacts_bidirectionally(sender, instance, action, reverse, **kwargs):
    """
    Asegura que si un usuario agrega a otro a su lista de contactos,
    la relación se cree también en sentido inverso.

    - Si se añade un contacto, también se añade la relación inversa.
    - Si se elimina un contacto, se elimina también la relación inversa.
    """
    if action == "post_add":  # Cuando se agregan contactos
        for user in instance.allowed_users.all():
            # Busca o crea la lista de contactos del usuario agregado
            restricted_contacts, created = AllowedContacts.objects.get_or_create(user=user)
            
            # Si el usuario actual no está ya en la lista del otro, lo agrega
            if instance.user not in restricted_contacts.allowed_users.all():
                restricted_contacts.allowed_users.add(instance.user)

    elif action == "post_remove":  # Cuando se eliminan contactos
        # Recorre los usuarios que todavía tienen a instance.user como contacto
        for user in User.objects.filter(restricted_contacts__allowed_users=instance.user):
            # Si el usuario ya no está en la lista actual, elimina la relación inversa
            if user not in instance.allowed_users.all():
                user.restricted_contacts.allowed_users.remove(instance.user)



@receiver(post_save, sender=UserSystemRole)
def assign_all_permissions_to_new_role(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo rol, se le asigna a todos los roles automáticamente todos los tipos de permisos
    con allowed=True (bloqueados por defecto).
    """
    if created:
        for permission in PermissionType.objects.all():
            RolePermission.objects.create(
                role=instance,
                permission_type=permission,
                allowed=True  # bloqueado por defecto
            )
