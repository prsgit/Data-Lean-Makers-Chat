from django.apps import AppConfig


class AppsmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appSMS'

    def ready(self):
        import appSMS.signals
