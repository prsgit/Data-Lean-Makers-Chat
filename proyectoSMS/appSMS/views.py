import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from appSMS.permissions import get_visible_contacts, has_group_permission, has_permission
from .models import GroupMessageReadStatus, Message, GroupChat, GroupMessage, PushSubscription, UserProfile,  MessageReadStatus
from PIL import Image
from django.utils.text import slugify
from django.utils.timezone import now
import re
import json


User = get_user_model()


def home(request):
    return render(request, 'appSMS/home.html')


# def login_view(request):
#     if request.user.is_authenticated:
#         # Redirige a la sala de chat si ya está autenticado
#         # Pasar el username del usuario autenticado
#         return redirect(f'/chat/{username}/?primer_acceso=true')

#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 login(request, user)
#                 request.session['primer_acceso'] = True
#                 # Redirige a la nueva URL de sala de chat después de iniciar sesión
#                 # Pasar el username del usuario autenticado
#                 return redirect('appSMS:chat_privado', username=username)
#             else:
#                 messages.error(
#                     request, "Nombre de usuario o contraseña incorrectos.")
#                 return redirect('appSMS:login')
#     else:
#         form = AuthenticationForm()

#     return render(request, 'appSMS/login.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        # Redirige a la sala de chat si ya está autenticado
        # Pasar el username del usuario autenticado
        return redirect('appSMS:chat_privado', username=request.user.username)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # Redirige a la nueva URL de sala de chat después de iniciar sesión
                # Pasar el username del usuario autenticado
                return redirect('appSMS:chat_privado', username=username)
            else:
                messages.error(
                    request, "Nombre de usuario o contraseña incorrectos.")
                return redirect('appSMS:login')
    else:
        form = AuthenticationForm()

    return render(request, 'appSMS/login.html', {'form': form})



# def registro(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')

#         # Validación de la contraseña
#         if password != confirm_password:
#             messages.error(request, "Las contraseñas no coinciden.")
#             return redirect('appSMS:registro')

#         try:
#             # Crear el usuario
#             user = User.objects.create_user(
#                 username=username, password=password)
#             user.save()
#             messages.success(
#                 request, "Usuario creado con éxito. Puedes iniciar sesión.")
#             return redirect('appSMS:login')
#         except Exception as e:
#             messages.error(
#                 request, "Error al crear el usuario: {}".format(str(e)))
#             return redirect('appSMS:registro')

#     return render(request, 'appSMS/registro.html')


# cambiar imagen de perfil de un usuario
@login_required
def update_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        if avatar:
            try:
                # Verificar si el archivo subido es una imagen válida
                img = Image.open(avatar)
                img.verify()
                # Guardar el nuevo avatar
                user_profile.avatar = avatar
                user_profile.save()
                # Redirigir al chat privado después de una actualización exitosa
                return redirect('appSMS:chat_privado', username=request.user.username)
            except (IOError, SyntaxError):
                # Mensaje de error si el archivo no es válido
                messages.error(
                    request, 'Por favor, sube un archivo de imagen válido.')
        else:
            messages.error(
                request, 'Por favor, selecciona un archivo para subir.')

    # Renderizar la página de actualización para solicitudes GET o en caso de error
    return render(request, 'appSMS/update_profile.html', {'user_profile': user_profile})


# cambiar imagen de perfil de un grupo
@login_required
def update_group_avatar(request, group_id):

    try:
        # Obtener el grupo por su ID
        group = GroupChat.objects.get(id=group_id)
    except GroupChat.DoesNotExist:
        messages.error(request, "El grupo no existe.")
        return redirect('appSMS:chat_grupal', group_name=slugify(group.name))

    if request.method == 'POST':
        avatar = request.FILES.get('avatar')  # Captura el archivo subido
        if avatar:
            try:
                # Valida si el archivo es una imagen válida usando Pillow
                img = Image.open(avatar)
                img.verify()  # Verifica que es una imagen válida

                # Guardar el nuevo avatar del grupo
                group.avatar = avatar
                group.save()

                return redirect('appSMS:chat_grupal', group_name=slugify(group.name))
            except (IOError, SyntaxError):
                # Maneja el caso en que el archivo no sea una imagen válida
                messages.error(
                    request, 'Por favor, sube un archivo de imagen válido.')
        else:
            # Caso en que no se seleccione un archivo
            messages.error(
                request, 'Por favor, selecciona un archivo para subir.')

    # Renderizar la página de actualización para solicitudes GET o en caso de error
    return render(request, 'appSMS/update_profile_group.html', {'group': group})


# Chat entre dos usuarios
@login_required
def chat_privado(request, username=None):
    
    users = get_visible_contacts(request.user)
    groups = GroupChat.objects.filter(members=request.user)

    for user in users:
        unread_count = MessageReadStatus.objects.filter(
            message__sender=user,
            message__receiver=request.user,
            read=False
        ).count()
        user.unread_count = unread_count
    
    for g in groups: # recorremos cada grupo al que pertenece el usuario para calcular su contador de mensajes no leídos grupo por grupo
        unread_count = GroupMessageReadStatus.objects.filter( # filtra los registros de lectura de ese grupo
            user=request.user, # usuario actual
            message__group=g, # grupo actual
            read=False # estado de lectura
        ).count()
        g.unread_count = unread_count



    # Convertir nombres de grupos a formato correcto
    for g in groups:
        g.display_name = g.name.replace('-', ' ').title()

    if username:
        try:
            other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('appSMS:login')

        # para se pueda chatear con uno mismo
        if username == request.user.username:
            room_name = f'private_chat_{request.user.id}_{request.user.id}'
        else:
            # ordena los ids de los usuarios
            user_ids = sorted([request.user.id, other_user.id])
            # crea el nombre de la sala de chat
            room_name = f'private_chat_{user_ids[0]}_{user_ids[1]}'
            
        # verifica si el usuario tiene activado el permiso "escribir" en un grupo
        if has_permission(request.user, "escribir"):
            messages =  Message.objects.none()    # no mostrar mensajes si el permiso escribir está bloqueado
        else:
            # Filtrar mensajes que no han sido eliminados por el usuario actual
            messages = Message.objects.filter(
            room_name=room_name
            ).exclude(
            sender=request.user, sender_deleted=True
            ).exclude(
            receiver=request.user, receiver_deleted=True
            ).exclude(
            deleted_for_all=True
            ).order_by('timestamp')

        if other_user:
            # Marcar como leídos todos los mensajes recibidos de este usuario
            MessageReadStatus.objects.filter(
                user=request.user,
                message__sender=other_user,
                read=False
            ).update(
                read=True,
                date_read = now()         
            )


        if request.method == "POST":
            content = request.POST.get("content", "").strip()
            file = request.FILES.get("file")
            if content or file:
                Message.objects.create(
                    room_name=room_name,
                    sender=request.user,
                    receiver=other_user,
                    content=content,
                    file=file
                )
                response = redirect('appSMS:chat_privado', username=username)

                return response

    else:
        other_user = None
        room_name = None
        messages = []

    return render(request, 'appSMS/sala.html', {
        'users': users,
        'other_user': other_user,
        'messages': messages,
        'room_name': room_name,
        'groups': groups,
        'selected_group': None,
    })


@csrf_exempt
def marcar_mensaje_leido(request, message_id):
    if request.method == "POST":
        MessageReadStatus.objects.filter(
            message_id=message_id,
            user=request.user,
            read=False
        ).update(read=True, date_read=now())
        return JsonResponse({"status": "ok"})
    
    return JsonResponse({"status": "error"}, status=400)


# @login_required
# def chat_privado(request, username=None):
#     # Obtener el valor de la sesión
#     primer_acceso = request.session.get('primer_acceso', False)
    
#     # Limpiar la sesión después de usar
#     if primer_acceso:
#         request.session['primer_acceso'] = False
    
#     users = get_visible_contacts(request.user)
#     groups = GroupChat.objects.filter(members=request.user)


#     # Convertir nombres de grupos a formato correcto
#     for g in groups:
#         g.display_name = g.name.replace('-', ' ').title()

#     if username:
#         try:
#             other_user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return redirect('appSMS:login')

#         # para se pueda chatear con uno mismo
#         if username == request.user.username:
#             room_name = f'private_chat_{request.user.id}_{request.user.id}'
#         else:
#             # ordena los ids de los usuarios
#             user_ids = sorted([request.user.id, other_user.id])
#             # crea el nombre de la sala de chat
#             room_name = f'private_chat_{user_ids[0]}_{user_ids[1]}'

#         # Filtrar mensajes que no han sido eliminados por el usuario actual
#         messages = Message.objects.filter(
#             room_name=room_name
#         ).exclude(
#             sender=request.user, sender_deleted=True
#         ).exclude(
#             receiver=request.user, receiver_deleted=True
#         ).exclude(
#             deleted_for_all=True
#         ).order_by('timestamp')

#         if request.method == "POST":
#             content = request.POST.get("content", "").strip()
#             file = request.FILES.get("file")
#             if content or file:
#                 Message.objects.create(
#                     room_name=room_name,
#                     sender=request.user,
#                     receiver=other_user,
#                     content=content,
#                     file=file
#                 )
#                 response = redirect('appSMS:chat_privado', username=username)
#                 return response

#     else:
#         other_user = None
#         room_name = None
#         messages = []

#     return render(request, 'appSMS/sala.html', {
#         'users': users,
#         'other_user': other_user,
#         'messages': messages,
#         'room_name': room_name,
#         'groups': groups,
#         'selected_group': None,
#         'primer_acceso': primer_acceso  # Pasar el valor a la plantilla
#     })

@login_required
def logout_view(request):
    logout(request)
    return redirect('appSMS:home')


@login_required
def create_group(request):
    
    if request.method == "POST":
        # Captura el nombre del grupo y normaliza el nombre a formato slug
        group_name = request.POST.get("group_name").strip()
        normalized_name = slugify(group_name)

        # Captura los IDs de los miembros seleccionados
        members = request.POST.getlist("members")
        # Captura el archivo del avatar subido
        avatar = request.FILES.get("avatar")

        # Valida si se seleccionaron miembros
        if not members:
            messages.error(request, "Debes elegir al menos un miembro")
            return redirect('appSMS:crear_grupo')

        # Valida si el grupo ya existe usando el nombre normalizado
        if GroupChat.objects.filter(name=normalized_name).exists():
            messages.error(request, "El grupo ya existe, prueba con otro nombre")    
            return redirect('appSMS:crear_grupo')

        # Valida si el archivo subido es una imagen válida
        if avatar:
            try:
                img = Image.open(avatar)
                img.verify()  # Verifica si el archivo es una imagen válida
            except (IOError, SyntaxError):
                messages.error(
                    request, 'Por favor, sube un archivo de imagen válido.')
                return redirect('appSMS:crear_grupo')

        # Crea el grupo con el nombre normalizado
        group = GroupChat(
            name=normalized_name,
            creator=request.user,
            avatar=avatar if avatar else "group_avatars/default_group.png"  # imagen por defecto
        )
        group.save()  # Guarda el grupo en la base de datos

        # Añade al usuario creador como miembro
        group.members.add(request.user)
        # Añadir los demás miembros seleccionados
        group.members.add(*User.objects.filter(id__in=members))

        # Redirige al chat grupal usando el nombre normalizado
        return redirect('appSMS:chat_grupal', group_name=normalized_name)

    else:  # Si no es POST, asumimos que es GET
        # Usuarios disponibles para agregar al grupo (excluyendo al creador y al admin)
        users = User.objects.exclude(id=request.user.id).exclude(username='admin')   
        return render(request, 'appSMS/create_group.html', {'users': users})


# Chat para grupos
@login_required
def group_chat(request, group_name):

    group = get_object_or_404(GroupChat, name=slugify(group_name))

    # Marcar como leídos todos los mensajes del grupo para el usuario actual
    GroupMessageReadStatus.objects.filter(
        user=request.user,
        message__group=group,
        read=False
    ).update(
        read=True, 
        date_read=now()
    )


    group_display_name = group.name.replace('-', ' ').title()

    users = get_visible_contacts(request.user)
    groups = GroupChat.objects.filter(members=request.user)

    for g in groups: # recorremos cada grupo al que pertenece el usuario para calcular su contador de mensajes no leídos grupo por grupo
        unread_count = GroupMessageReadStatus.objects.filter( # filtra los registros de lectura de ese grupo
            user=request.user, # usuario actual
            message__group=g, # grupo actual
            read=False # estado de lectura
        ).count()
        g.unread_count = unread_count
    
    for user in users:
        unread_count = MessageReadStatus.objects.filter(
            message__sender=user,
            message__receiver=request.user,
            read=False
        ).count()
        user.unread_count = unread_count


    for g in groups:
        g.display_name = g.name.replace('-', ' ').title()

    # verifica si el usuario tiene activado el permiso "escribir" en un grupo
    if has_group_permission(request.user, group, "escribir"):
        messages = []  # no se le muestran mensajes
    else:
        messages = GroupMessage.objects.filter(
        group=group
        ).exclude(
        deleted_by=request.user
        ).exclude(
        deleted_for_all=True
        ).order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        file = request.FILES.get("file")
        if content or file:
            GroupMessage.objects.create(
                group=group,
                sender=request.user,
                content=content,
                file=file
            )
            # Usar response para evitar múltiples llamadas
            response = redirect('appSMS:chat_grupal', group_name=slugify(group.name))
                               
            return response

    return render(request, 'appSMS/sala.html', {
        'users': users,
        'messages': messages,
        'room_name': f'group_chat_{group.id}',
        'groups': groups,
        'selected_group': group,
        'group_display_name': group_display_name
    })



@csrf_exempt
def marcar_mensaje_leido_grupo(request, group_name):
    if request.method == "POST":
        try:
            group = GroupChat.objects.get(name=group_name)
        except GroupChat.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Grupo no encontrado"}, status=404)

        GroupMessageReadStatus.objects.filter(
            user=request.user,
            message__group=group,
            read=False
        ).update(read=True, date_read=now()) #marca como leídos todos los mensajes no leídos en ese grupo para ese usuario

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=400)


# vaciado del chat individual completo
@login_required
def delete_chat(request, room_name):
    if request.method == 'POST':
        # Marcar los mensajes como eliminados por el usuario actual
        Message.objects.filter(room_name=room_name,
                               sender=request.user).update(sender_deleted=True)
        Message.objects.filter(room_name=room_name, receiver=request.user).update(
            receiver_deleted=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# vaciado del chat grupal completo
logger = logging.getLogger(__name__)
@login_required
def delete_group_chat(request, group_name):
    if request.method == 'POST':
        logger.info(f"Nombre del grupo recibido: {group_name}")
        try:
            group = get_object_or_404(
                GroupChat, name=group_name.replace('-', ' '))
            messages = GroupMessage.objects.filter(group=group)
            for message in messages:
                message.deleted_by.add(request.user)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error al eliminar chat: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# elimina sms uno a uno en el chat individual
@login_required
def delete_private_message(request, message_id):
    if request.method == 'POST':
        try:
            message = Message.objects.get(id=message_id)
            if message.sender == request.user:
                message.sender_deleted = True
            elif message.receiver == request.user:
                message.receiver_deleted = True
            else:
                return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)

            message.deleted_by = request.user
            message.deleted_date = now()

            message.save()

            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mensaje no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# elimina sms uno a uno en el chat grupal
@login_required
def delete_group_message(request, message_id):
    if request.method == 'POST':
        try:
            # Buscar el mensaje por su ID
            message = GroupMessage.objects.get(id=message_id)

            # Comprobar si el usuario es miembro del grupo
            if request.user in message.group.members.all():

                # Marcar el mensaje como eliminado para el usuario actual
                message.deleted_by.add(request.user)
                message.deleted_date = now()

                message.save()

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)
        except GroupMessage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mensaje no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@csrf_exempt
@login_required
def save_subscription(request):
    if request.method == "POST":
        data = json.loads(request.body)
        subscription, created = PushSubscription.objects.get_or_create(
            user=request.user,
            endpoint=data["endpoint"],
            defaults={
                "p256dh": data["keys"]["p256dh"],
                "auth": data["keys"]["auth"],
            },
        )
        if not created:
            subscription.p256dh = data["keys"]["p256dh"]
            subscription.auth = data["keys"]["auth"]
            subscription.save()

        return JsonResponse({"mensaje": "Suscripción guardada correctamente."})
    return JsonResponse({"error": "Solicitud inválida"}, status=400)


# elimina un sms para ambos usuarios en el chat individual
@login_required
def delete_private_message_for_all(request, message_id):
    if request.method == 'POST':
        try:
            message = Message.objects.get(id=message_id)

            if message.sender != request.user:
                return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)

            message.deleted_for_all = True  # Marcar el mensaje como eliminado para todos
            message.deleted_by = request.user
            message.deleted_date = now()

            message.save()

            # Emitir evento al WebSocket
            channel_layer = get_channel_layer()
            room_name = message.room_name  # Nombre de la sala de chat
            async_to_sync(channel_layer.group_send)(
                f'chat_{room_name}',
                {
                    'type': 'delete_message_for_all',
                    'message_id': message_id,
                    'file_url': message.file.url if message.file else None,
                }
            )

            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mensaje no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# elimina un sms para todos los usuarios en el chat grupal
@login_required
def delete_group_message_for_all(request, message_id):
    if request.method == 'POST':
        try:
            message = GroupMessage.objects.get(id=message_id)

            if message.sender != request.user or request.user not in message.group.members.all():
                return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)

            # Marcar el mensaje como eliminado para todos
            message.deleted_for_all = True
            message.deleted_by.add(request.user)
            message.deleted_date = now()

            message.save()

            # Emitir evento al WebSocket
            channel_layer = get_channel_layer()
            # Nombre del grupo de WebSocket
            group_name = f"group_chat_{re.sub(r'[^a-zA-Z0-9._-]', '_', message.group.name)}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'delete_message_for_all',
                    'message_id': message_id,
                    'file_url': message.file.url if message.file else None,
                }
            )

            return JsonResponse({'status': 'success'})
        except GroupMessage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mensaje no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
