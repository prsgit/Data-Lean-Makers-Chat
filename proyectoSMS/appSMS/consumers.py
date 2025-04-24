import json
import os
import re  # Importamos re para limpieza de texto
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.conf import settings
from .models import GroupMessageReadStatus, Message, GroupChat, GroupMessage, MessageReadStatus
from appSMS.utils import send_push_notification
from appSMS.permissions import has_permission, get_anonymous_role, has_group_permission, get_anonymous_group_role

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        print(f"Intentando conectar: usuario={self.user}")

        if not self.user.is_authenticated:
            print("Usuario no autenticado, cerrando conexión")
            await self.close()
            return

        try:
            self.group = await database_sync_to_async(GroupChat.objects.get)(name=self.room_name)
            self.room_group_name = f"group_chat_{re.sub(r'[^a-zA-Z0-9._-]', '_', self.room_name)}"
            print(f"Conectado al chat grupal: {self.group.name}")
        except GroupChat.DoesNotExist:
            self.room_group_name = f"chat_{self.room_name}"
            self.group = None
            print(f"Conectado al chat privado: {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add( 
            f"user_{self.user.id}",
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')
        user = self.scope['user']

        if self.group:
            # Para grupos: verificamos permisos de grupo
            leer_activado = await database_sync_to_async(has_group_permission)(user, self.group, "leer")
            escribir_activado = await database_sync_to_async(has_group_permission)(user, self.group, "escribir")
        else:
            # Para chats individuales: verificamos permisos globales
            leer_activado = await database_sync_to_async(has_permission)(user, "leer")
            escribir_activado = await database_sync_to_async(has_permission)(user, "escribir")

        if leer_activado or escribir_activado:
            await self.send(text_data=json.dumps({
                "type": "sistema",
                "message": "⚠️ No tienes permiso para escribir ni enviar archivos"
            }))
            return

        # Manejar eventos de eliminación para mí
        if event_type == 'delete_for_me':
            message_id = data.get('message_id')
            await self.channel_layer.group_send(
                self.room_group_name,  # Enviar el evento al grupo correspondiente
                {
                    'type': 'delete_message_for_me',
                    'message_id': message_id,
                    'user': self.user.username,  # solo afecta solo al emisor
                }
            )
            return

        # Manejar eventos de eliminación global
        if event_type == 'delete_for_all':
            message_id = data.get('message_id')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_message_for_all',
                    'message_id': message_id,
                }
            )
            return

        # Lógica existente para enviar mensajes
        message = data.get('message', '')
        file_url = data.get('file_url', None)
        sender = self.user

        if file_url:
            file_url = await self.save_file(file_url, is_group_chat=bool(self.group))


        # Verificar si tiene permiso anónimo en el grupo
        is_anonymous = await database_sync_to_async(has_group_permission)(sender, self.group, "anonimo")

        sender_alias = None
        if is_anonymous:
            role_with_alias = await database_sync_to_async(get_anonymous_group_role)(sender, self.group)
            if role_with_alias:
                alias_name = role_with_alias.name  # Ej: "Soporte"
                sender_alias = f"{alias_name}_{sender.username}"

        # Guardar el mensaje en grupo con alias si aplica
        if self.group:
            message_instance = await database_sync_to_async(GroupMessage.objects.create)(
                group=self.group,
                sender=sender,
                content=message,
                file=file_url,
                sender_alias=sender_alias
            )
            print(
                f"Mensaje enviado al grupo {self.room_name} por {sender.username}")
            
            # crea registros de lectura para todos los miembros del grupo (excepto el emisor)
            members = await database_sync_to_async(list)( self.group.members.exclude(id=sender.id))         

            for member in members:
                await database_sync_to_async(GroupMessageReadStatus.objects.create)(
                    user=member,
                    message=message_instance,
                    read=False
                )

            # cuenta el número de mensajes no leídos que tiene este miembro en este grupo
            unread_count = await database_sync_to_async(
                lambda: GroupMessageReadStatus.objects.filter(
                    user=member,
                    read=False,
                    message__group=self.group
                ).count()
            )() # ejecuta la función anónima lambda

            # enviar al usuario el nuevo contador de mensajes no leídos para actualizar su globito
            await self.channel_layer.group_send(
                f"user_{member.id}",  # canal individual del receptor
                {
                    'type': 'update_unread_group_count',
                    'unread_count': unread_count,
                    'group_name': self.group.name,
                }
            )

            if sender_alias:
                display_name = sender_alias.split("_")[0]
            else:
                display_name = sender.username

            members = await database_sync_to_async(list)(self.group.members.exclude(id=sender.id))
            for member in members:
                payload = {
                    "title": f"Mensaje de {display_name} en el grupo {self.group.name.replace('-', ' ').title()}",
                    "body": message if message else "Has recibido un archivo.",
                    "icon": "/static/img/icon192.png",
                    "url": f"/chat/{self.group.name}/"
                }
                await database_sync_to_async(send_push_notification)(member, payload)

        else:
            room_name_parts = self.room_name.split('_')
            user_ids = [int(uid) for uid in room_name_parts if uid.isdigit()]
            other_users = [uid for uid in user_ids if uid != sender.id]
            other_user_id = other_users[0] if other_users else sender.id
            receiver = await database_sync_to_async(User.objects.get)(id=other_user_id)

            #Verifica si el usuario tiene activado el permiso "anonimo"
            is_anonymous = await database_sync_to_async(has_permission)(sender, "anonimo")

            # Inicializa el alias como None
            sender_alias = None

            # Si el permiso está activado, busca el rol que lo tiene
            if is_anonymous:
                role_with_alias = await database_sync_to_async(get_anonymous_role)(sender)

                if role_with_alias:
                    alias_name = role_with_alias.name  # Ej: "Soporte"
                    sender_alias = f"{alias_name}_{sender.username}"  # Ej: "Soporte_Pedro"


            message_instance = await database_sync_to_async(Message.objects.create)(
                room_name=self.room_name,
                sender=sender,
                receiver=receiver,
                content=message,
                file=file_url,
                sender_alias=sender_alias
            )
            print(
                f"Mensaje enviado al usuario {receiver.username} en la sala {self.room_name}")
            
            await database_sync_to_async(MessageReadStatus.objects.create)(
                user=receiver,         # el usuario que tiene que leer el mensaje
                message=message_instance,  # el mensaje que acaba de ser enviado
                read=False             # estado inicial: no leído
            )

            # calcula el nuevo contador de mensajes no leídos para el receptor
            unread_count = await database_sync_to_async(
                lambda: MessageReadStatus.objects.filter(
                    user=receiver,
                    read=False,
                    message__sender=sender
                ).count()
            )()

            # envía el nuevo contador de mensajes no leídos al receptor
            await self.channel_layer.group_send(
                f"user_{receiver.id}",  # canal individual del receptor
                {
                    'type': 'update_unread_count',
                    'unread_count': unread_count,
                    'sender_username': sender.username,
                }
            )

            if sender_alias:
                display_name = sender_alias.split("_")[0]
            else:
                display_name = sender.username
                
            payload = {
                "title": f"Mensaje de {display_name}",
                "body": message if message else "Has recibido un archivo.",
                "icon": "/static/img/icon192.png",
                "url": f"/chat/{sender.username}/"
            }
            await database_sync_to_async(send_push_notification)(receiver, payload)

       
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_username': display_name, # muestra el alias
                'sender_realname': sender.username, # muestra el nombre real
                'file_url': file_url,
                'message_id': message_instance.id,

            }
        )

    async def chat_message(self, event):
        if self.group:
            permiso_denegado = await database_sync_to_async(has_group_permission)(self.user, self.group, "escribir")
        else:
            permiso_denegado = await database_sync_to_async(has_permission)(self.user, "escribir")

        if permiso_denegado:
            return # ignora el mensaje y no lo envía

        message = event['message']
        sender_username = event['sender_username']
        file_url = event.get('file_url', None)
        message_id = event.get('message_id', None)

        if file_url and not file_url.startswith(settings.MEDIA_URL):
            file_url = f"{settings.MEDIA_URL}{file_url}"

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_username,
            'sender_realname': event['sender_realname'],
            'file_url': file_url,
            'message_id': message_id
        }))

    async def delete_message_for_all(self, event):
        message_id = event['message_id']
        file_url = event.get('file_url')

        await self.send(text_data=json.dumps({
            'type': 'delete_for_all',
            'message_id': message_id,
            'file_url': file_url,
        }))

    async def delete_message_for_me(self, event):
        message_id = event['message_id']  # ID del mensaje que se elimina
        user = event['user']  # Usuario que solicita la eliminación

        # Enviar el evento solo al usuario que lo eliminó
        if user == self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'delete_for_me',
                'message_id': message_id,
            }))

    async def save_file(self, file_data, is_group_chat):
        format, imgstr = file_data.split(';base64,')
        ext = format.split('/')[-1]
        folder = 'group_files' if is_group_chat else 'private_files'
        folder_path = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{self.user.username}_{self.room_name}_{int(self.channel_name[-6:], 36)}.{ext}"
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(imgstr))

        return f"{folder}/{filename}"


    async def force_disconnect(self, event):
        """
        Desconecta al usuario cuando se desactiva su cuenta desde el admin.
        """
        await self.send(text_data=json.dumps({
            "type": "sistema",
            "message": event.get("message", "Has sido desconectado.")
    }))
        await self.close()


    async def update_unread_count(self, event):
        unread_count = event['unread_count'] # extrae el número de mensajes por leer
        sender_username = event['sender_username'] # extrae al usuario que envío el sms para ponerle el globito en la lista de usuarios del receptor

        await self.send(text_data=json.dumps({
            'type': 'update_unread_count',
            'unread_count': unread_count,
            'sender_username': sender_username,
        }))


    async def update_unread_group_count(self, event):
        unread_count = event['unread_count']  # número de mensajes no leídos en el grupo
        group_name = event['group_name']      # nombre del grupo

    # Enviar al cliente WebSocket del usuario
        await self.send(text_data=json.dumps({
            'type': 'update_unread_group_count',
            'unread_count': unread_count,
            'group_name': group_name,
        }))
