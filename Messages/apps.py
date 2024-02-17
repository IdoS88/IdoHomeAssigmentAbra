from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Messages'
    def ready(self):
        from .signals import handle_message_receiver_delete
        # Import the signals module