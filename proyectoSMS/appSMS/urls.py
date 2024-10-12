from django.urls import path
from . import views

app_name = 'appSMS'

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/<str:username>/', views.chat_privado, name='chat_privado'),
]
