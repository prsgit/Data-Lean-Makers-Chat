from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message


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

    if username:
        try:
            other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('appSMS:login')

        # Genera un nombre de sala único basado en los IDs de usuario
        user_ids = sorted([request.user.id, other_user.id])
        room_name = f'private_chat_{user_ids[0]}_{user_ids[1]}'

        # Obtener mensajes previos
        messages = Message.objects.filter(
            room_name=room_name).order_by('timestamp')
    else:
        other_user = None
        room_name = None
        messages = []

    return render(request, 'appSMS/sala.html', {
        'users': users,
        'other_user': other_user,
        'messages': messages,
        'room_name': room_name,
    })


# a falta de modificar el html este código es para que pueda enviar sms asi mismo tambien
# @login_required
# def chat_privado(request, username=None):
#     User = get_user_model()

#     # Obtener lista de usuarios disponibles + el logeado, menos el admin.
#     users = User.objects.exclude(username='admin')

#     # Si el usuario se conecta a la sala
#     if username:
#         try:
#             other_user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return redirect('appSMS:login')

#         # Generar un nombre de sala único basado en los IDs de usuario
#         user_ids = sorted([request.user.id, other_user.id])
#         room_name = f'private_chat_{user_ids[0]}_{user_ids[1]}'

#         # Obtener mensajes previos
#         messages = Message.objects.filter(
#             room_name=room_name).order_by('timestamp')

#         # Manejar el envío de mensajes
#         if request.method == 'POST':
#             content = request.POST.get('content')
#             if content:
#                 # Guardar mensaje en la base de datos (puede ser a sí mismo o a otro usuario)
#                 Message.objects.create(
#                     room_name=room_name,
#                     sender=request.user,
#                     receiver=other_user if other_user != request.user else request.user,
#                     content=content
#                 )
#                 # Actualizar los mensajes después de enviar
#                 messages = Message.objects.filter(
#                     room_name=room_name).order_by('timestamp')

#     else:
#         other_user = None
#         room_name = None
#         messages = []

#     return render(request, 'appSMS/sala.html', {
#         'users': users,
#         'other_user': other_user,
#         'messages': messages,
#         'room_name': room_name,
#     })


@login_required
def logout_view(request):
    logout(request)
    return redirect('appSMS:home')
