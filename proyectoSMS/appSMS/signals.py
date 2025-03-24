from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile,ExternalUserContacts, UserRole

User = get_user_model()

# cuando creamos un perfil nuevo se agrega automáticamente el UserProfile de models.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente para un usuario nuevo.
    """
    if created:  # Solo ejecuta esto al crear un usuario nuevo
        UserProfile.objects.create(user=instance)
        print(f"Perfil creado para el usuario: {instance.username}")



# para hacer que los contactos sean bidireccionales automáticamente, ExternalUserContacts de models.py
@receiver(m2m_changed, sender=ExternalUserContacts.allowed_users.through)
def sync_contacts_bidirectionally(sender, instance, action, reverse, **kwargs):
    """
    Asegura que  si un usuario externo agrega otro usuario a su lista de contactos,
    aparezcan en las dos listas de usuarios.
    """
    if action == "post_add":  # cuando se agregan contactos
        for user in instance.allowed_users.all():
            if UserRole.objects.filter(user=user, role="externo").exists():  # solo si el usuario es externo
                contact_list, created = ExternalUserContacts.objects.get_or_create(external_user=user) #  busca si el usuario agregado tiene una lista de contactos y si no la tiene la crea.
                if instance.external_user not in contact_list.allowed_users.all():
                    contact_list.allowed_users.add(instance.external_user) # agrega al usuario actual en la lista del otro.

    elif action == "post_remove":  # cuando se eliminan contactos
        for user in User.objects.filter(contact_list__allowed_users=instance.external_user): # recorre sobre todos los usuarios que todavía tienen a instance.external_user en su lista de contactos.
            if user not in instance.allowed_users.all(): # verifica si el usuario sigue n la lista de contactos
                user.contact_list.allowed_users.remove(instance.external_user) # lo elimina en ambas lista de contactos