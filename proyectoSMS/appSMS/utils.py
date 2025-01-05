import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from appSMS.models import PushSubscription

def send_push_notification(user, payload):
    """
    Envía una notificación push a un usuario específico.

    :param user: Usuario destinatario de la notificación.
    :param payload: Diccionario con los datos de la notificación (title, body, icon, url).
    """
    # Buscar la suscripción push del usuario
    subscription = PushSubscription.objects.filter(user=user).first()

    if subscription:
        try:
            # Enviar la notificación usando pywebpush
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth,
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:pedrorueda.develop@gmail.com" 
                }
            )
            print(f"Notificación enviada a {user.username} con éxito.")
        except WebPushException as ex:
            print(f"Error al enviar la notificación a {user.username}: {ex}")
    else:
        print(f"No se encontró una suscripción para el usuario {user.username}.")
