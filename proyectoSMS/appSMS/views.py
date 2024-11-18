from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message,GroupChat, GroupMessage


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
    User = get_user_model()

    # Obtener lista de usuarios disponibles + el logeado, menos el admin.
    users = User.objects.exclude(username='admin')

    # Obtener los grupos en los que el usuario está asociado
    groups = GroupChat.objects.filter(members=request.user)

    if username:
        try:
            other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('appSMS:login')

        # Genera un nombre de sala único basado en los IDs de usuario
        if username == request.user.username:
            # Si el usuario está enviando un mensaje a sí mismo
            room_name = f'private_chat_{request.user.id}_{request.user.id}'
        else:
            # Si el usuario está enviando un mensaje a otro usuario
            user_ids = sorted([request.user.id, other_user.id])
            room_name = f'private_chat_{user_ids[0]}_{user_ids[1]}'

        # Obtener mensajes previos
        messages = Message.objects.filter(room_name=room_name).order_by('timestamp')
    else:
        other_user = None
        room_name = None
        messages = []

    return render(request, 'appSMS/sala.html', {
        'users': users,
        'other_user': other_user,
        'messages': messages,
        'room_name': room_name,
        'groups': groups,  # Añadir grupos aquí
        'selected_group': None,  # O el grupo seleccionado si lo hay
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
        group.members.add(*User.objects.filter(id__in=members))  # Añade otros miembros
        
        return redirect('appSMS:chat_grupal', group_name=group.name)

    # Excluye al admin y al que está creando el grupo
    users = User.objects.exclude(id=request.user.id).exclude(username='admin') 
    return render(request, 'appSMS/create_group.html', {'users': users})

@login_required
def group_chat(request, group_name):
    group = get_object_or_404(GroupChat, name=group_name)

    if request.user not in group.members.all():
        return redirect('appSMS:group_list')  # Redirige a la lista de grupos si no es miembro del grupo 

    users = User.objects.exclude(username='admin')
    groups = GroupChat.objects.filter(members=request.user) # recupera los grupos del usuario
    messages = GroupMessage.objects.filter(group=group).order_by('timestamp') # recupera los sms asociados al grupo y los ordena por fecha

    if request.method == "POST":
        content = request.POST.get("content")
        if content:  # Verifica si el contenido no está vacío
            GroupMessage.objects.create(group=group, sender=request.user, content=content)
            messages.success(request, "Mensaje enviado con éxito.")
        else:
            messages.error(request, "No se puede enviar un mensaje vacío.")
        return redirect('appSMS:group_chat', group_name=group.name)

    return render(request, 'appSMS/sala.html', {
        'users': users,
        'messages': messages,
        'room_name': f'group_chat_{group.id}',
        'groups': groups,
        'selected_group': group,
    })
