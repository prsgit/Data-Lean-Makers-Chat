from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify


User = get_user_model()


class GroupChat(models.Model):
    name = models.CharField("Nombre del Grupo",max_length=255, unique=True)  # Nombre del grupo
    creator = models.ForeignKey(  # el creador
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_groups", verbose_name="Creador del Grupo"
    )
    members = models.ManyToManyField(
        User, related_name="group_chats", verbose_name="Miembros disponibles")
    avatar = models.ImageField(
        upload_to='group_avatars/', default='group_avatars/default_group.png', verbose_name="Imagen del Grupo")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Convierte el nombre en slug antes de guardarlo
        self.name = slugify(self.name)
        super(GroupChat, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(
        GroupChat, on_delete=models.CASCADE, related_name="messages", verbose_name="Nombre del Grupo")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Enviado por")
    content = models.TextField("Contenido del Mensaje",blank=True, null=True)
    file = models.FileField("Archivo Adjunto",upload_to="group_files/", blank=True, null=True)
    timestamp = models.DateTimeField("Fecha y Hora de Envío",auto_now_add=True)
    deleted_by = models.ManyToManyField(
        User, related_name='deleted_group_messages', blank=True, verbose_name="Eliminado por")
    deleted_for_all = models.BooleanField("Eliminado para todos", default=False)
    deleted_date = models.DateTimeField("Fecha de eliminación",null=True, blank=True)

    def __str__(self):
        return f'{self.sender} to {self.group.name}: {self.content[:50]}'


class Message(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Enviado por")
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', verbose_name="Recibido por")
    content = models.TextField("Contenido del mensaje",blank=True, null=True)
    file = models.FileField("Archivo Adjunto",upload_to="private_files/", blank=True, null=True)
    timestamp = models.DateTimeField("Fecha y Hora de envío", auto_now_add=True)
    sender_deleted = models.BooleanField("Eliminado por el remitente",default=False)
    receiver_deleted = models.BooleanField("Eliminado por el destinatario",default=False)
    deleted_for_all = models.BooleanField("Eliminado para todos",default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_messages', verbose_name="Eliminado por"
    )
    deleted_date = models.DateTimeField("Fecha de eliminación",null=True, blank=True)

    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.content}'


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.URLField()
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscripción para el usuario: {self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='avatars/', default='avatars/default.png')

    def __str__(self):
        return self.user.username


class UserRole(models.Model):
    ROLE_CHOICES = [
        ('interno', 'Interno'),
        ('externo', 'Externo'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def clean(self):
        # se obtiene todos los roles actuales del usuario
        roles_asignados = [r.role for r in self.user.roles.all()]

        # verifica que el usuario al menos tenga un rol, Interno o Externo
        if 'interno' not in roles_asignados and 'externo' not in roles_asignados:
            raise ValidationError(
                "El usuario debe tener al menos un rol: Interno o Externo.")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


# lista de contactos del usuario con rol externo (con quien puede hablar)
class ExternalUserContacts(models.Model):

    external_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="contact_list",
        limit_choices_to=Q(roles__role="externo"),
        verbose_name="Usuario Externo"
    )

    allowed_users = models.ManyToManyField(  # lista de usuarios con los que el usuario externo podrá chatear
        User,
        related_name="contacted_by",
        blank=True,
        verbose_name="Usuarios permitidos"
    )

    class Meta:
        verbose_name = "External contact"
        verbose_name_plural = "External contacts"

    def __str__(self):
        return f"Contactos de {self.external_user.username}"

