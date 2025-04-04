from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()


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


# roles
class UserSystemRole(models.Model):
    name = models.CharField(max_length=50,unique=True,verbose_name="Rol")
    description = models.TextField(max_length=255,verbose_name="Descripción",blank=True )

    def __str__(self):
        # nombre del rol en lugar de "UserSystemRole"
        return self.name
    class Meta:
        verbose_name = "Roles del sistema"
        verbose_name_plural = "Roles del sistema"

# asignar rol
class UserRoleAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_roles")
    role = models.ForeignKey(UserSystemRole, on_delete=models.CASCADE, related_name="assigned_users")

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    

# tipo de permisos
class PermissionType(models.Model):
    code = models.SlugField(max_length=50, unique=True, null=False, blank=False,  verbose_name="Código", help_text="Identificador técnico del permiso (no cambiar una vez creado)")
    name = models.CharField(max_length=50, unique=True, verbose_name="Permiso")
    description = models.TextField(max_length=200, blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Tipos de permisos"
        verbose_name_plural = "Tipos de permisos"

    def __str__(self):
        return self.name


# permisos para los roles
class RolePermission(models.Model):
    role = models.ForeignKey(UserSystemRole,on_delete=models.CASCADE,related_name='permissions', verbose_name="Rol")
    permission_type = models.ForeignKey(PermissionType,on_delete=models.CASCADE,related_name='roles', verbose_name="Tipo de permiso")
    allowed = models.BooleanField(default=True, verbose_name="Bloqueado") # si el permiso está permitido o no
    class Meta:
        unique_together = ('role', 'permission_type') # evita duplicados
        verbose_name = "Permisos rol"
        verbose_name_plural = "Permisos rol"

    def __str__(self):
        estado = "Permitido" if self.allowed else "Denegado"
        return f"{self.role.name} - {self.permission_type.name}: {estado}"



# lista de contactos del usuario con rol externo (con quien puede hablar)
class AllowedContacts(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="restricted_contacts",
        verbose_name="Usuarios"
    )

    allowed_users = models.ManyToManyField(  # lista de usuarios con los que el usuario externo podrá chatear
        User,
        related_name="visible_for_users",
        blank=True,
        verbose_name="Usuarios permitidos"
    )

    class Meta:
        verbose_name = "Contactos asignados"
        verbose_name_plural = "Contactos asignados"

    def __str__(self):
        return f"Contactos permitidos para {self.user.username}"


class Message(models.Model):
    room_name = models.CharField("Sala de chat", max_length=255)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Enviado por")
    sender_alias = models.CharField(max_length=150, blank=True, null=True, help_text="Nombre que se muestra al enviar el mensaje si el usuario es anónimo"
 )
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
    
    class Meta:
        verbose_name = "Mensajes de los chat"
        verbose_name_plural = "Mensajes de los chats"

    
class GroupChat(models.Model):
    name = models.CharField("Nombre del Grupo",max_length=255, unique=True)  # Nombre del grupo
    creator = models.ForeignKey(  # el creador
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_groups", verbose_name="Creador del Grupo"
    )
    members = models.ManyToManyField(
        User, related_name="group_chats", verbose_name="Miembros disponibles")
    avatar = models.ImageField(
        upload_to='group_avatars/', default='group_avatars/default_group.png', verbose_name="Imagen del Grupo")
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    def save(self, *args, **kwargs):
        # Convierte el nombre en slug antes de guardarlo
        self.name = slugify(self.name)
        super(GroupChat, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Grupos de chats"
        verbose_name_plural = "Grupos de chats"


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
    
    class Meta:
        verbose_name = "Mensajes de grupos"
        verbose_name_plural = "Mensajes de grupos"



