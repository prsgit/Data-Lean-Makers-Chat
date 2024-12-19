from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Message, GroupChat, GroupMessage
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
            user_ids = sorted([request.user.id, other_user.id]) # ordena los ids de los usuarios
            room_name = f'private_chat_{user_ids[0]}_{user_ids[1]}'# crea el nombre de la sala de chat

        # Filtrar mensajes que no han sido eliminados por el usuario actual
        messages = Message.objects.filter(
            room_name=room_name
        ).exclude(
            sender=request.user, sender_deleted=True
        ).exclude(
            receiver=request.user, receiver_deleted=True
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
                return redirect('appSMS:chat_privado', username=username)

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
        group_name = request.POST.get("group_name")
        members = request.POST.getlist("members")

        # Verificar si se ha seleccionado al menos un miembro
        if not members:
            messages.error(request, "Debes elegir al menos un miembro")
            return redirect('appSMS:crear_grupo')

        # Verificar si el grupo ya existe
        if GroupChat.objects.filter(name=group_name).exists():
            messages.error(request, "El grupo ya existe.")
            return redirect('appSMS:crear_grupo')

        # Crear el nuevo grupo si no existe
        group = GroupChat.objects.create(name=group_name)
        group.members.add(request.user)  # Añade al creador
        # Añade otros miembros
        group.members.add(*User.objects.filter(id__in=members))

        return redirect('appSMS:chat_grupal', group_name=group.name)

    # Excluye al admin y al que está creando el grupo
    users = User.objects.exclude(id=request.user.id).exclude(username='admin')
    return render(request, 'appSMS/create_group.html', {'users': users})


@login_required
def group_chat(request, group_name):
    group = get_object_or_404(GroupChat, name=group_name)

    if request.user not in group.members.all():
        return redirect('appSMS:group_list')

    users = User.objects.exclude(username='admin')
    groups = GroupChat.objects.filter(members=request.user)
    messages = GroupMessage.objects.filter(group=group).exclude(deleted_by=request.user).order_by('timestamp')

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
            return redirect('appSMS:chat_grupal', group_name=group.name)

    return render(request, 'appSMS/sala.html', {
        'users': users,
        'messages': messages,
        'room_name': f'group_chat_{group.id}',
        'groups': groups,
        'selected_group': group,
    })


@login_required
def delete_chat(request, room_name):
    if request.method == 'POST':
        # Marcar los mensajes como eliminados por el usuario actual
        Message.objects.filter(room_name=room_name, sender=request.user).update(sender_deleted=True)
        Message.objects.filter(room_name=room_name, receiver=request.user).update(receiver_deleted=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def delete_group_chat(request, group_name):
    if request.method == 'POST':
        group = get_object_or_404(GroupChat, name=group_name)
        messages = GroupMessage.objects.filter(group=group)
        for message in messages:
            message.deleted_by.add(request.user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


