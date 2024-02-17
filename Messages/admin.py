# Register your models here.
from django.contrib import admin

from .models import Users, MessageItemInfo, MessageReceivers

admin.site.register(Users)
admin.site.register(MessageItemInfo)
admin.site.register(MessageReceivers)
