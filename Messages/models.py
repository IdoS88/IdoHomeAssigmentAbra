# Create your models here.
import uuid

from django.contrib.auth.models import User
from django.db import models


# class Users(models.Model):
#     username = models.CharField(primary_key=True, max_length=25)
#     password = models.CharField(max_length=30, editable=True)
#
#     def __str__(self):
#         return f'\nusername: {self.username} \npassword: {self.password}\n'
#

class MessageItemInfo(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    subject = models.CharField(max_length=35)
    text = models.TextField()
    dateCreated = models.DateField(auto_now=True)

    def __str__(self):
        return f'\nMessage_id: {self.message_id} \nsender: {self.sender}\nsubject: {self.subject}\ntext: {self.text}\ndate_created: {self.dateCreated}\n'

    class Meta:
        constraints = [models.UniqueConstraint(fields=['message_id', 'sender'],
                                               name='unique_migration_host_combination_message_sender')]


class MessageReceivers(models.Model):
    message = models.ForeignKey(MessageItemInfo, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.PROTECT)
    read = models.BooleanField(editable=True, default=False)

    def __str__(self):
        return f'\nMessage_id: {self.message} \nreceiver: {self.receiver}\nread: {self.read}\n'

    class Meta:
        constraints = [models.UniqueConstraint(fields=['message', 'receiver'],
                                               name='unique_migration_host_combination_message_receiver')]
