from django.contrib import admin
from .models import Message, GroupChat, GroupMessage

admin.site.site_header = "Chat Data Lean Makers"


class MessageAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('sender', 'receiver', 'timestamp', 'content')
    list_filter = ('sender', 'receiver', 'timestamp')  # Filtros disponibles
    # Campos en los que se puede buscar
    search_fields = ('content', 'sender__username', 'receiver__username')
    # Ordenar por fecha, de más reciente a más antiguo
    ordering = ('-timestamp',)


admin.site.register(Message, MessageAdmin)


class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

admin.site.register(GroupChat, GroupChatAdmin)

class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'timestamp', 'content')
    list_filter = ('group', 'sender', 'timestamp')
    search_fields = ('content', 'sender__username')
    ordering = ('-timestamp',)

admin.site.register(GroupMessage, GroupMessageAdmin)
