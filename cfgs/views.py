from django.shortcuts import render
from django.http import HttpResponse
from .models import PT, DeviceType
from rest_framework import viewsets
from .serializers import PTSerializer, DeviceTypeSerializer
import csv

# Create your endpoints here.


class PTsViewSet(viewsets.ModelViewSet):
    pts = PT.objects.all()

    if len(pts) == 0:
        pts_source_data = "/home/carlos/kio/PITA/cfgs/sources/pts_data.csv"
        with open(pts_source_data) as data:
            reader = csv.reader(data, delimiter="|")
            for line in reader:
                pt = PT(vpn=line[0], name=line[1],
                        hostgroup=line[2], nagios_ip=line[3])
                pt.save()
    queryset = PT.objects.all()
    serializer_class = PTSerializer


class DeviceTypeViewSet(viewsets.ModelViewSet):
    types = DeviceType.objects.all()
    if len(types) == 0:
        types_source_data = "/home/carlos/kio/PITA/cfgs/sources/device_types.csv"
        with open(types_source_data) as data:
            reader = csv.reader(data)
            for line in reader:
                t = DeviceType(device_type=line[0])
                t.save()
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer


# class PTsInitializeViewSet(viewsets.ModelViewSet):
#     pts = PT.objects.all()
#     if len(pts) == 0:
#         pts_source_data = "sources/pts_data.csv"
#         with open(pts_source_data) as data:
#             reader = csv.reader(f, delimiter="|")
#             for line in reader:
#                 pt = PT(vpn=line[0], name=line[1],
#                         hostgroup=line[2], nagios_ip=line[3])
#                 p.save()
#     queryset = PT.objects.all()
#     serializer_class = PTSerializer
