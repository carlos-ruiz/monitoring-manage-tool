from django.contrib import admin

# Register your models here.
from .models import PT, DeviceType

admin.site.register(PT)
admin.site.register(DeviceType)
