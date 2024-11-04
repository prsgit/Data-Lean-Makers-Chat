import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Message, GroupChat, GroupMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # Asegúrate de que este valor es dinámico
        self.user = self.scope['user']
        print(f"Intentando conectar: usuario={self.user}")

        if not self.user.is_authenticated:
            print("Usuario no autenticado, cerrando conexión")
            await self.close()
            return

        # Determinar si es un chat grupal o privado comprobando la existencia del grupo
        try:
            # Intentamos obtener un grupo con el nombre de la sala
            self.group = await database_sync_to_async(GroupChat.objects.get)(name=self.room_name)
            self.room_group_name = f"group_chat_{self.room_name}"
            print(f"Conectado al chat grupal: {self.group.name}")
        except GroupChat.DoesNotExist:
            # Si no existe el grupo, asumimos que es un chat privado
            self.room_group_name = f"chat_{self.room_name}"
            self.group = None
            print(f"Conectado al chat privado: {self.room_group_name}")

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Usuario {self.user.username} conectado a la sala {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Usuario {self.user.username} desconectado de la sala {self.room_group_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        sender = self.user
        User = get_user_model()

        # Verificar si estamos en un chat grupal o privado
        if self.group:
            # Lógica para mensajes grupales
            await database_sync_to_async(GroupMessage.objects.create)(
                group=self.group,
                sender=sender,
                content=message
            )
            print(f"Mensaje enviado al grupo {self.room_name} por {sender.username}")
        else:
            # Lógica para mensajes privados (separando IDs de usuarios)
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
            print(f"Mensaje enviado al usuario {receiver.username} en la sala {self.room_name}")

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


#ESTE CÓDIGO FALLA , NO GUARDA LOS SMS ENVIADOS POR UN GRUPO.
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth import get_user_model
# from channels.db import database_sync_to_async
# from .models import Message, GroupChat, GroupMessage

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']  
#         self.user = self.scope['user']
#         print(f"Intentando conectar: usuario={self.user}")

#         if not self.user.is_authenticated:
#             print("Usuario no autenticado, cerrando conexión")
#             await self.close()
#             return

#         # Determinar si es un chat grupal o privado
#         if "group" in self.room_name:
#             self.room_group_name = f"group_chat_{self.room_name}"
#             print(f"Conectando al chat grupal: {self.room_group_name}")

#             # Intenta obtener el grupo existente
#             try:
#                 self.group = await database_sync_to_async(GroupChat.objects.get)(name=self.room_name)
#                 print(f"Grupo '{self.room_name}' encontrado.")
#             except GroupChat.DoesNotExist:
#                 print(f"El grupo '{self.room_name}' no existe. Cerrando conexión.")
#                 await self.close()
#                 return
#         else:
#             self.room_group_name = f"chat_{self.room_name}"
#             print(f"Conectando al chat privado: {self.room_group_name}")

#         # Unirse al grupo
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#         print(f"Usuario {self.user.username} conectado a la sala {self.room_group_name}")

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#         print(f"Usuario {self.user.username} desconectado de la sala {self.room_group_name}")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data.get('message', '')
#         sender = self.user
#         User = get_user_model()

#         # Verificar si es un grupo o un chat privado
#         if "group" in self.room_group_name:
#             print(f"Grupo actual: {self.group}")  # Verifica el grupo aquí

#             # Crear el mensaje del grupo
#             await database_sync_to_async(GroupMessage.objects.create)(
#                 group=self.group,
#                 sender=sender,
#                 content=message
#             )
#             print(f"Mensaje enviado a grupo {self.room_name} por {sender.username}")
#         else:
#             room_name_parts = self.room_name.split('_')
#             user_ids = [int(uid) for uid in room_name_parts if uid.isdigit()]
#             other_users = [uid for uid in user_ids if uid != sender.id]
#             other_user_id = other_users[0] if other_users else sender.id
#             receiver = await database_sync_to_async(User.objects.get)(id=other_user_id)

#             await database_sync_to_async(Message.objects.create)(
#                 room_name=self.room_name,
#                 sender=sender,
#                 receiver=receiver,
#                 content=message
#             )
#             print(f"Mensaje enviado al grupo {self.room_name} por el usuario {sender.username}")

#         # Enviar el mensaje al grupo
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'sender_username': sender.username
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         sender_username = event['sender_username']

#         await self.send(text_data=json.dumps({
#             'message': message,
#             'sender': sender_username
#         }))