import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        print(f"Intentando conectar: usuario={self.user}")

        if not self.user.is_authenticated:
            print("Usuario no autenticado, cerrando conexión")
            await self.close()
            return

        room_name_parts = self.room_name.split('_')
        if str(self.user.id) not in room_name_parts:
            print(
                f"Usuario {self.user.username} no tiene permiso para unirse a la sala {self.room_name}, cerrando conexión")
            await self.close()
            return

        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(
            f"Usuario {self.user.username} conectado a la sala {self.room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        sender = self.user

        User = get_user_model()

        # Obtener los IDs de usuario del nombre de la sala
        room_name_parts = self.room_name.split('_')
        user_ids = [int(uid) for uid in room_name_parts if uid.isdigit()]

        # Encontrar el ID del otro usuario
        other_user_id = [uid for uid in user_ids if uid != sender.id][0]

        # Obtener el objeto del otro usuario
        receiver = await database_sync_to_async(User.objects.get)(id=other_user_id)

        # Guardar el mensaje en la base de datos
        await database_sync_to_async(Message.objects.create)(
            room_name=self.room_name,
            sender=sender,
            receiver=receiver,
            content=message
        )

        # Enviar el mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_username': sender.username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender_username']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_username
        }))
