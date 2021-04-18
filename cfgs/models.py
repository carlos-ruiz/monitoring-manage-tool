from django.db import models

# Create your models here.


class DeviceType(models.Model):
    device_type = models.CharField(max_length=50)
    nagiosDeviceHostgroup = models.CharField(max_length=50, default='')

    def __str__(self):
        return "{0} - {1}".format(self.device_type, self.nagiosDeviceHostgroup)


class PT(models.Model):
    name = models.CharField(max_length=256)
    vpn = models.CharField(max_length=10, primary_key=True)
    hostgroup = models.CharField(max_length=256)
    nagios_ip = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.name


class File(models.Model):
    file = models.FileField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class CFG(models.Model):
    vpn = models.ForeignKey(PT, on_delete=models.CASCADE)
    folder = models.CharField(max_length=50)
    file = models.CharField(max_length=50)
    hostgroup = models.ForeignKey(DeviceType, on_delete=models.CASCADE)

    def __str__(self):
        return self.file
