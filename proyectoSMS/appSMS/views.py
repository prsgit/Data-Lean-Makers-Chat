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
from .models import Message, GroupChat, GroupMessage, PushSubscription, UserProfile
from appSMS.utils import send_push_notification
from PIL import Image
from django.conf import settings
import os
import json

User = get_user_model()


def home(request):
    return render(request, 'appSMS/home.html')


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


def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validación de la contraseña
        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('appSMS:registro')

        try:
            # Crear el usuario
            user = User.objects.create_user(
                username=username, password=password)
            user.save()
            messages.success(
                request, "Usuario creado con éxito. Puedes iniciar sesión.")
            return redirect('appSMS:login')
        except Exception as e:
            messages.error(
                request, "Error al crear el usuario: {}".format(str(e)))
            return redirect('appSMS:registro')

    return render(request, 'appSMS/registro.html')


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
        return redirect('appSMS:chat_grupal', group_name=group.name)

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

                return redirect('appSMS:chat_grupal', group_name=group.name)
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


@login_required
def chat_privado(request, username=None):
    users = User.objects.exclude(username='admin')
    groups = GroupChat.objects.filter(members=request.user)

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

                payload = {
                    "title": f"Nuevo mensaje de {request.user.username}",
                    "body": content if content else "Has recibido un archivo.",
                    "icon": "/static/img/icon192.png",
                    "url": f"/chat/{request.user.username}/",
                    "group": False
                }
                send_push_notification(other_user, payload)

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


@login_required
def logout_view(request):
    logout(request)
    return redirect('appSMS:home')


@login_required
def group_list(request):
    # Filtrar los grupos en los que el usuario es miembro
    groups = GroupChat.objects.filter(members=request.user)

    # Renderizar la plantilla con la lista de grupos
    return render(request, 'appSMS/group_list.html', {'groups': groups})


@login_required
def create_group(request):
    if request.method == "POST":

        # Captura el nombre del grupo
        group_name = request.POST.get("group_name")
        # Captura los IDs de los miembros seleccionados
        members = request.POST.getlist("members")
        # Captura el archivo del avatar subido
        avatar = request.FILES.get("avatar")

        # Valida si se seleccionaron miembros
        if not members:
            messages.error(request, "Debes elegir al menos un miembro")
            return redirect('appSMS:crear_grupo')

        # Valida si el grupo ya existe
        if GroupChat.objects.filter(name=group_name).exists():
            messages.error(request, "El grupo ya existe.")
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

        # Crea el grupo
        group = GroupChat(
            name=group_name,
            avatar=avatar if avatar else "group_avatars/default_group.png"  # imagen por defecto
        )
        group.save()  # Guarda el grupo en la base de datos

        # Añade al usuario creador como miembro
        group.members.add(request.user)
        # Añadir los demás miembros seleccionados
        group.members.add(*User.objects.filter(id__in=members))

        # Redirige al chat grupal
        return redirect('appSMS:chat_grupal', group_name=group.name)

    else:  # Si no es POST, asumimos que es GET
        # Usuarios disponibles para agregar al grupo (excluyendo al creador y al admin)
        users = User.objects.exclude(
            id=request.user.id).exclude(username='admin')
        return render(request, 'appSMS/create_group.html', {'users': users})


@login_required
def group_chat(request, group_name):
    group = get_object_or_404(GroupChat, name=group_name)

    if request.user not in group.members.all():
        return redirect('appSMS:group_list')

    users = User.objects.exclude(username='admin')
    groups = GroupChat.objects.filter(members=request.user)
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

            # Crear el payload para la notificación
            payload = {
                "title": f"Nuevo mensaje en {group.name}",
                "body": content if content else "Has recibido un archivo.",
                "icon": "/static/img/icon192.png",
                "url": f"/group/{group_name}/",
                "group": True
            }

            # Enviar notificaciones push a todos los miembros del grupo excepto al remitente
            for member in group.members.exclude(id=request.user.id):
                send_push_notification(member, payload)

            # Usar response para evitar múltiples llamadas
            response = redirect('appSMS:chat_grupal', group_name=group.name)
            return response

    return render(request, 'appSMS/sala.html', {
        'users': users,
        'messages': messages,
        'room_name': f'group_chat_{group.id}',
        'groups': groups,
        'selected_group': group,
    })


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
@login_required
def delete_group_chat(request, group_name):
    if request.method == 'POST':
        group = get_object_or_404(GroupChat, name=group_name)
        messages = GroupMessage.objects.filter(group=group)
        for message in messages:
            message.deleted_by.add(request.user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


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

            # Marcar el mensaje como eliminado para todos
            message.deleted_for_all = True
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
            message.save()

            # Emitir evento al WebSocket
            channel_layer = get_channel_layer()
            # Nombre del grupo de WebSocket
            group_name = f"group_chat_{message.group.name}"
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
