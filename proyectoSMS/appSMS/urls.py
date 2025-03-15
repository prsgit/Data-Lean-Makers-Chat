from django.urls import path
from . import views

app_name = 'appSMS'

urlpatterns = [
    path('', views.home, name='home'),
    # path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/<str:username>/', views.chat_privado, name='chat_privado'),
    path('crear_grupo/', views.create_group, name='crear_grupo'),
    path('grupo_chat/<slug:group_name>/', views.group_chat, name='chat_grupal'),
    path('delete_chat/<str:room_name>/', views.delete_chat, name='delete_chat'),
    path('delete_group_chat/<str:group_name>/', views.delete_group_chat, name='delete_group_chat'),
    path('save-subscription/', views.save_subscription, name='save_subscription'),
    path('delete_private_message/<int:message_id>/', views.delete_private_message, name='delete_private_message'),
    path('delete_group_message/<int:message_id>/', views.delete_group_message, name='delete_group_message'),
    path('delete_private_message_for_all/<int:message_id>/', views.delete_private_message_for_all, name='delete_private_message_for_all'),
    path('delete_group_message_for_all/<int:message_id>/', views.delete_group_message_for_all, name='delete_group_message_for_all'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('group/<int:group_id>/update_avatar/', views.update_group_avatar, name='update_group_avatar'),
]
