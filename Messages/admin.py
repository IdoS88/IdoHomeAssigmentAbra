# Register your models here.
from django.contrib import admin

from .models import MessageItemInfo, MessageReceivers

admin.site.register(MessageItemInfo)
admin.site.register(MessageReceivers)
