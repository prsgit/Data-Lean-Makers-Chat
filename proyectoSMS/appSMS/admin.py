from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import UserSystemRole, UserRoleAssignment, PermissionType, RolePermission, AllowedContacts, Message, GroupChat, GroupMessage

admin.site.site_header = "Chat Data Lean Makers"


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    can_delete = False # no se podrán eliminar desde aquí
    readonly_fields = ['permission_type']  # Solo lectura
    fields = ['permission_type', 'allowed']  # Orden y visibilidad
 
@admin.register(UserSystemRole)
class UserSystemRoleAdmin(admin.ModelAdmin): # listado de roles
    list_display = ('name', 'description')
    inlines = [RolePermissionInline]
class UserRoleAssignmentInline(admin.TabularInline):# asignar roles a los usuarios
    model = UserRoleAssignment
    extra = 1 # fila para agregar un rol adicional

class CustomUserAdmin(UserAdmin):
    inlines = [UserRoleAssignmentInline] # extendemos aqui la clase UserRoleAssignmentInline

    list_display = ('username', 'email', 'get_roles', 'is_staff', 'is_superuser')

    def get_roles(self, obj):
        roles = obj.assigned_roles.select_related('role')
        return ", ".join([assignment.role.name for assignment in roles])

    get_roles.short_description = "Roles"

admin.site.unregister(User)  # Quitamos el admin de usuarios predeterminado
admin.site.register(User, CustomUserAdmin)  # Registrar versión personalizada



@admin.register(PermissionType)
class PermissionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission_type', 'allowed')
    list_filter = ('role', 'permission_type', 'allowed')
    search_fields = ('role__name', 'permission_type__name')  # buscar por nombre del rol o permiso



# lista de contactos permitidos
@admin.register(AllowedContacts)
class AllowedContactsAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_allowed_users')
    filter_horizontal = ('allowed_users',) # para seleccionar varios usuarios permitidos
    ordering = ('user',) 

    def get_user(self, obj): # esta función accede al username del usuario
        return obj.user.username

    get_user.short_description = "Usuario"

    def get_allowed_users(self, obj): # esta función muestra todos los usuarios permitidos
        return ", ".join([user.username for user in obj.allowed_users.all()])

    get_allowed_users.short_description = "Usuarios Permitidos"


# mensajes en chat entre dos usuarios
class MessageAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('sender_with_alias', 'receiver', 'timestamp',
                    'content', 'deleted_by', 'deleted_for_all', 'deleted_date')
    list_filter = ('sender', 'receiver', 'timestamp', 'deleted_by')
    # Campos en los que se puede buscar
    search_fields = ('content', 'sender__username', 'receiver__username')
    # Ordenar por fecha, de más reciente a más antiguo
    ordering = ('-timestamp',)

    def sender_with_alias(self, obj):
        """
        Muestra el alias si existe (ej: Soporte_Dani),
        o el nombre real del remitente si no tiene alias.
        """
        return obj.sender_alias if obj.sender_alias else obj.sender.username

    sender_with_alias.short_description = 'Enviado por'


admin.site.register(Message, MessageAdmin)


# grupos de chat
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'display_members')
    search_fields = ('name',)
    ordering = ('-created_at',) 

    def display_members(self, obj):
        return ", ".join([user.username for user in obj.members.all()])

    display_members.short_description = "Miembros"


admin.site.register(GroupChat, GroupChatAdmin,)


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
