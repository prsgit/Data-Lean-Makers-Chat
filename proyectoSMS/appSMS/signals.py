from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente para un usuario nuevo.
    """
    if created:  # Solo ejecuta esto al crear un usuario nuevo
        UserProfile.objects.create(user=instance)
        print(f"Perfil creado para el usuario: {instance.username}")
