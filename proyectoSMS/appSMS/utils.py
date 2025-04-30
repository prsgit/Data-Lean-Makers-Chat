from pywebpush import webpush, WebPushException
from django.db import DatabaseError
import json
from django.conf import settings
from appSMS.models import PushSubscription



def send_push_notification(user, payload):
    subscriptions = PushSubscription.objects.filter(user=user)

    for subscription in subscriptions:
        try:
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
            print(f"Notificación enviada a {user.username}")
        except WebPushException as ex:
            print(f"Error al enviar push a {user.username}: {ex}")
            #  Elimina suscripciones inválidas automáticamente
            if "404" in str(ex) or "410" in str(ex):
                try:
                    subscription.delete()
                    print(f"Suscripción inválida eliminada para {user.username}")
                except DatabaseError as db_err:
                    print(f"Error al eliminar suscripción: {db_err}")