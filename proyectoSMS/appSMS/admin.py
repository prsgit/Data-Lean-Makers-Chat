from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.hashers import make_password
from .models import UserRole, ExternalUserContacts, Message, GroupChat, GroupMessage

admin.site.site_header = "Chat Data Lean Makers"


class UserRoleInline(admin.TabularInline):
    """Permite seleccionar roles al crear un usuario en el administrador."""
    model = UserRole
    extra = 0  # No mostrar filas vacías para agregar nuevos roles
    can_delete = False  # no se elimina el rol desde aquí
    max_num = 1  # Un usuario solo puede recibir un rol en la creación


class CustomUserCreationForm(forms.ModelForm):
    """Extiende el formulario de creación de usuario para incluir la selección de roles (Interno o Externo)."""
    role = forms.ChoiceField(
        choices=UserRole.ROLE_CHOICES,  # lista filtrada
        required=True,
        label="Rol"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def save(self, commit=True):
        """Guarda el usuario y le asigna el rol seleccionado antes de guardarlo completamente."""
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])

        user.save()  # Guardamos el usuario primero para asegurarnos de que tiene un ID

    # Creamos el rol manualmente
        UserRole.objects.create(user=user, role=self.cleaned_data["role"])

        return user


class CustomUserAdmin(UserAdmin):
    """Personaliza Django Admin para que el formulario de creación solo permita Interno o Externo."""

    add_form = CustomUserCreationForm  # formulario personalizado.

    add_fieldsets = ( # lo que solicita al crear un usuario.
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'role'),
        }),
    )
    
    """edición de rol"""
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # si el usuario ya existe (modo edición)
            self.inlines = [UserRoleInline]
        else:  # si es nuevo, no mostrar inlines
            self.inlines = []
        return form

    list_display = ('username', 'email', 'get_roles','is_staff', 'is_superuser')
                    

    def get_roles(self, obj):

        # Buscamos los roles asignados al usuario
        roles = UserRole.objects.filter(user=obj)
        # Mostrar los roles
        return ", ".join([role.get_role_display() for role in roles])

    get_roles.short_description = "Roles"


admin.site.unregister(User)  # Quitamos el admin de usuarios predeterminado
admin.site.register(User, CustomUserAdmin)  # Registrar versión personalizada


# lista de contactos para usuarios con rol externo
@admin.register(ExternalUserContacts)
class externalUserContactAdmin(admin.ModelAdmin):
    list_display = ('external_user', 'get_allowed_users')
    filter_horizontal = ('allowed_users',)
    ordering = ('external_user',) 

    def get_external_user(self, obj):
        return obj.external_user.username

    get_external_user.short_description = "Usuario Externo"

    def get_allowed_users(self, obj):
        return ", ".join([user.username for user in obj.allowed_users.all()])

    get_allowed_users.short_description = "Usuarios Permitidos"


# mensajes en chat entre dos usuarios
class MessageAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('sender', 'receiver', 'timestamp',
                    'content', 'deleted_by', 'deleted_for_all', 'deleted_date')
    list_filter = ('sender', 'receiver', 'timestamp', 'deleted_by')
    # Campos en los que se puede buscar
    search_fields = ('content', 'sender__username', 'receiver__username')
    # Ordenar por fecha, de más reciente a más antiguo
    ordering = ('-timestamp',)


admin.site.register(Message, MessageAdmin)


# grupos de chat
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'display_members')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def display_members(self, obj):
        return ", ".join([user.username for user in obj.members.all()])

    display_members.short_description = "Miembros"


admin.site.register(GroupChat, GroupChatAdmin)


# mensajes de grupos de chat
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'timestamp', 'content',
                    'display_deleted_by', 'deleted_for_all', 'deleted_date')
    list_filter = ('group', 'sender', 'timestamp', 'deleted_for_all')
    search_fields = ('content', 'sender__username')
    ordering = ('-timestamp',)

    def display_deleted_by(self, obj):
        return ", ".join([user.username for user in obj.deleted_by.all()])

    display_deleted_by.short_description = "Deleted by"


admin.site.register(GroupMessage, GroupMessageAdmin)
