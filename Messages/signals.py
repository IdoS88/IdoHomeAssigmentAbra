from django.conf import settings
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .models import MessageReceivers, MessageItemInfo


@receiver(post_delete, sender=MessageReceivers)
def handle_message_receiver_delete(sender, instance, **kwargs):
    message_info = instance.message_id
    if not MessageReceivers.objects.filter(message_id=message_info).exists():
        MessageItemInfo.objects.filter(pk=message_info).delete()  # Delete MessageItemInfo if all unread receivers gone


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
