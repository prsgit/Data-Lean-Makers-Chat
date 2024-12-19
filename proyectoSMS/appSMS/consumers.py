import json
import os
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.conf import settings
from .models import Message, GroupChat, GroupMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self): #recupera la información de la sala y el usuario
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        print(f"Intentando conectar: usuario={self.user}")

        if not self.user.is_authenticated:
            print("Usuario no autenticado, cerrando conexión")
            await self.close()
            return

        try: #comprobación de si es un chat grupal o privado
            self.group = await database_sync_to_async(GroupChat.objects.get)(name=self.room_name)
            self.room_group_name = f"group_chat_{self.room_name}"
            print(f"Conectado al chat grupal: {self.group.name}")
        except GroupChat.DoesNotExist:
            self.room_group_name = f"chat_{self.room_name}"
            self.group = None
            print(f"Conectado al chat privado: {self.room_group_name}")

        await self.channel_layer.group_add( #conecta al usuario al grupo correspondiente en el canal de WebSocket y acepta la conexión
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(
            f"Usuario {self.user.username} conectado a la sala {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(
            f"Usuario {self.user.username} desconectado de la sala {self.room_group_name}")

    async def receive(self, text_data): #el servidor recibe datos enviados desde el cliente a través de websocket
        data = json.loads(text_data)
        message = data.get('message', '')
        file_url = data.get('file_url', None)
        sender = self.user

        # Guardar archivo si se envió
        if file_url:
            file_url = await self.save_file(file_url, is_group_chat=bool(self.group))

        # Guardar mensaje en la base de datos
        if self.group:
            await database_sync_to_async(GroupMessage.objects.create)(
                group=self.group,
                sender=sender,
                content=message,
                file=file_url
            )
            print(
                f"Mensaje enviado al grupo {self.room_name} por {sender.username}")
        else:
            room_name_parts = self.room_name.split('_') #divide el nombre de la sala en partes
            user_ids = [int(uid) for uid in room_name_parts if uid.isdigit()] #extrae los ids de los usuarios
            other_users = [uid for uid in user_ids if uid != sender.id] #filtra los ids de los usuarios que no son el remitente
            other_user_id = other_users[0] if other_users else sender.id #obtiene el id del usuario receptor
            receiver = await database_sync_to_async(User.objects.get)(id=other_user_id) #recupera el usuario receptor

            await database_sync_to_async(Message.objects.create)(
                room_name=self.room_name,
                sender=sender,
                receiver=receiver,
                content=message,
                file=file_url
            )
            print(
                f"Mensaje enviado al usuario {receiver.username} en la sala {self.room_name}")

        await self.channel_layer.group_send( #envía un mensaje a todos los miembros del canal (grupal o individual)
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_username': sender.username,
                'file_url': file_url
            }
        )

    async def chat_message(self, event): #se encarga de distribuir los mensajes los clientes conectados
        message = event['message']
        sender_username = event['sender_username']
        file_url = event.get('file_url', None)

        # concatenar `MEDIA_URL` si es necesario
        if file_url and not file_url.startswith(settings.MEDIA_URL): #comprueba si el archivo tiene el prefijo de la url de media
            file_url = f"{settings.MEDIA_URL}{file_url}" #si no tiene el prefijo, lo concatena

        #envía el mensaje al cliente
        await self.send(text_data=json.dumps({ #dumps:convierte un diccionario en una cadena JSON
            'message': message,
            'sender': sender_username,
            'file_url': file_url
        }))

    #guarda el archivo recibido y retorna su URL
    async def save_file(self, file_data, is_group_chat):
        format, imgstr = file_data.split(';base64,') #separa el formato y la cadena base64
        ext = format.split('/')[-1] #extrae la extensión del archivo
        folder = 'group_files' if is_group_chat else 'private_files' #determina la carpeta de destino
        folder_path = os.path.join(settings.MEDIA_ROOT, folder) #ruta de la carpeta de destino
        os.makedirs(folder_path, exist_ok=True) #crea la carpeta si no existe

        #crea un nombre único para el archivo
        filename = f"{self.user.username}_{self.room_name}_{int(self.channel_name[-6:], 36)}.{ext}" #genera un nombre único para el archivo
        file_path = os.path.join(folder_path, filename) #ruta completa del archivo

        #decodifica y guarda el archivo
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(imgstr)) 

        #retorna la ruta dentro de `MEDIA_URL`
        return f"{folder}/{filename}"
