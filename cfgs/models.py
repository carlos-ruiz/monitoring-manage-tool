from django.db import models

# Create your models here.


class DeviceType(models.Model):
    device_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class PT(models.Model):
    name = models.CharField(max_length=256)
    vpn = models.IntegerField()
    hostgroup = models.CharField(max_length=256)
    nagios_ip = models.CharField(max_length=16)

    def __str__(self):
        return self.name
