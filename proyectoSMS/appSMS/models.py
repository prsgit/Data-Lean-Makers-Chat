from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()


class GroupChat(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Nombre del grupo
    members = models.ManyToManyField(
        User, related_name="group_chats")  # Miembros del grupo
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="group_files/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ManyToManyField(User, related_name='deleted_group_messages', blank=True)

    def __str__(self):
        return f'{self.sender} to {self.group.name}: {self.content[:50]}'


class Message(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="private_files/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender_deleted = models.BooleanField(default=False)
    receiver_deleted = models.BooleanField(default=False)

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