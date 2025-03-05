from django.contrib import admin
from .models import Message, GroupChat, GroupMessage

admin.site.site_header = "Chat Data Lean Makers"


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


class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'display_members')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def display_members(self, obj):
        return ", ".join([user.username for user in obj.members.all()])

    display_members.short_description = "Members"


admin.site.register(GroupChat, GroupChatAdmin)


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
