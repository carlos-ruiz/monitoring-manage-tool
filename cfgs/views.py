from django.shortcuts import render
from django.http import HttpResponse
from .models import PT, DeviceType
from rest_framework import viewsets
from .serializers import PTSerializer, DeviceTypeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import csv
from PITA.settings import BASE_DIR

# Create your endpoints here.


class PTsViewSet(viewsets.ModelViewSet):
    queryset = PT.objects.all()
    serializer_class = PTSerializer

    @action(detail=False, methods=['post'], name="PTs Initialize")
    def pts_init(self, request):
        pts = PT.objects.all()

        if len(pts) == 0:
            pts_source_data = BASE_DIR+"/cfgs/sources/pts_data.csv"
            with open(pts_source_data) as data:
                reader = csv.reader(data, delimiter="|")
                for line in reader:
                    pt = PT(vpn=line[0], name=line[1],
                            hostgroup=line[2], nagios_ip=line[3])
                    pt.save()
        pts = PT.objects.all()
        serializer = self.get_serializer(pts, many=True)
        return Response(serializer.data)


class DeviceTypeViewSet(viewsets.ModelViewSet):
    types = DeviceType.objects.all()
    if len(types) == 0:
        types_source_data = BASE_DIR+"/cfgs/sources/device_types.csv"
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
