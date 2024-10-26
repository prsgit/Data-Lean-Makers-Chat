import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Message, GroupChat

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extrae el nombre de la sala y el usuario que intenta conectar
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        print(f"Intentando conectar: usuario={self.user}")

        # Verifica si el usuario está autenticado
        if not self.user.is_authenticated:
            print("Usuario no autenticado, cerrando conexión")
            await self.close()
            return

        # Verifica si la sala es un grupo o un chat privado
        if "group" in self.room_name:
            # Caso de grupo: Crea el nombre de grupo y permite el acceso
            self.room_group_name = f"group_chat_{self.room_name}"
            print(f"Conectando al chat grupal: {self.room_group_name}")
        else:
            # Caso de chat privado: Verifica si el usuario tiene permisos para unirse a la sala
            room_name_parts = self.room_name.split('_')
            if str(self.user.id) not in room_name_parts:
                print(f"Usuario {self.user.username} no tiene permiso para unirse a la sala {self.room_name}, cerrando conexión")
                await self.close()
                return
            self.room_group_name = f"chat_{self.room_name}"
            print(f"Conectando al chat privado: {self.room_group_name}")

        # Conectar al grupo del canal
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Usuario {self.user.username} conectado a la sala {self.room_group_name}")

    async def disconnect(self, close_code):
        # Desconectar el grupo del canal
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Usuario {self.user.username} desconectado de la sala {self.room_group_name}")

    async def receive(self, text_data):
        # Recibir el mensaje enviado desde el WebSocket
        data = json.loads(text_data)
        message = data.get('message', '')
        sender = self.user
        User = get_user_model()

        # Diferenciar entre chat grupal y privado para guardar el mensaje
        if "group" in self.room_group_name:
            # Si es un chat de grupo, asocia el mensaje al grupo
            group = await database_sync_to_async(GroupChat.objects.get)(name=self.room_name)
            await database_sync_to_async(GroupChat.objects.create)(
                group=group,
                sender=sender,
                content=message
            )
            print(f"Mensaje enviado a grupo {self.room_name} por {sender.username}")
        else:
            # Si es un chat privado, determina al receptor y guarda el mensaje
            room_name_parts = self.room_name.split('_')
            user_ids = [int(uid) for uid in room_name_parts if uid.isdigit()]
            other_users = [uid for uid in user_ids if uid != sender.id]

            other_user_id = other_users[0] if other_users else sender.id
            receiver = await database_sync_to_async(User.objects.get)(id=other_user_id)

            await database_sync_to_async(Message.objects.create)(
                room_name=self.room_name,
                sender=sender,
                receiver=receiver,
                content=message
            )
            print(f"Mensaje enviado a sala privada {self.room_name} de {sender.username} a {receiver.username}")

        # Envía el mensaje al grupo de WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_username': sender.username
            }
        )

    async def chat_message(self, event):
        # Maneja el evento para enviar mensajes al WebSocket del cliente
        message = event['message']
        sender_username = event['sender_username']

        # Envía el mensaje al cliente conectado
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_username
        }))
