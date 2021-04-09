from django.http import HttpResponse
from .models import PT, DeviceType, File
from rest_framework import viewsets
from .serializers import PTSerializer, DeviceTypeSerializer, FileSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import csv
from PITA.settings import BASE_DIR
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import shutil
import os
import json

# Create your endpoints here.


def chooseTemplate(templateType):
    template = ''
    if templateType == "linux":
        template = 'SVR-LINUX.cfg'
    elif templateType == 'windows':
        template = 'SVR-WINDOWS.cfg'
    elif templateType == 'switches':
        template = 'SWITCH.cfg'
    elif templateType == 'vv':
        template = 'SVR-VV.cfg'
    elif templateType == 'servers':
        template = 'SVR-TSM.cfg'
    elif templateType == 'ddi':
        template = 'SVR-DDI.cfg'
    elif templateType == 'fwmember':
        template = 'FW-MEMBER.cfg'
    elif templateType == 'fwcluster':
        template = 'FW-CLUSTER.cfg'

    return template


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
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer

    @action(detail=False, methods=['post'], name="Devices Type Initialize")
    def dt_init(self, request):
        types = DeviceType.objects.all()
        if len(types) == 0:
            types_source_data = str(BASE_DIR)+"/cfgs/sources/device_types.csv"
            with open(types_source_data) as data:
                reader = csv.reader(data)
                for line in reader:
                    t = DeviceType(
                        device_type=line[1], nagiosDeviceHostgroup=line[0])
                    t.save()
        types = DeviceType.objects.all()
        serializer = self.get_serializer(types, many=True)
        return Response(serializer.data)


class CFGsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], name='download template')
    def download_template(self, request):
        file_path = "/home/carlos/kio/PITA/cfgs/sources/template.csv"
        FilePointer = open(file_path, "r")
        response = HttpResponse(FilePointer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=template.csv'
        return response

    @action(detail=False, methods=['post'], name='Upload file')
    def upload_file(self, request, *args, **kwargs):
        parser_classes = (MultiPartParser, FormParser)
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], name='Generate file')
    def generate(self, request, *args, **kwargs):
        fileSource = request.data['filename']
        file_path = str(BASE_DIR)+str(fileSource)
        templatesPath = str(BASE_DIR)+'/cfgs/sources/templates-cfgs/'
        errors = []
        filesOK = []
        numOK = 0
        numFail = 0
        generatedPath = str(BASE_DIR)+'/cfgs/generated/'+fileSource[7:-4]+'/'
        print("File name {0}".format(generatedPath))
        try:
            if(os.path.isdir(generatedPath)):
                shutil.rmtree(generatedPath)
            os.mkdir(generatedPath)
        except:
            print("Error al borrar el folder: {0}".format(generatedPath))

        with open(file_path) as f:
            reader = csv.reader(f, delimiter=",")

            next(reader)
            for line in reader:
                template = templatesPath + chooseTemplate(line[3])
                hostname = line[1]
                ip = line[2]
                pt = PT.objects.get(vpn=line[0])
                hostgroup = pt.hostgroup
                newFileName = hostname+".cfg"

                if len(template) == 0:
                    print("No se encontró la plantilla para este tipo de equipo")
                    numFail += 1
                    errors.append(newFileName)
                    continue

                try:
                    with open(template) as tc:
                        t = tc.read()
                except:
                    print("No se puede leer la plantilla {0}".format(template))
                    numFail += 1
                    errors.append(newFileName)
                    continue

                with open(str(generatedPath)+str(newFileName), "w") as outfile:
                    t = t.replace("IPTOCHANGE", ip)
                    t = t.replace("HOSTNAMETOCHANGE", hostname)
                    t = t.replace("HOSTGROUPTOCHANGE", hostgroup)
                    try:
                        outfile.write(t)
                        numOK += 1
                        filesOK.append(newFileName)
                    except IOError as e:
                        print("Error al escribir el archivo %s" % e)
                        numFail += 1
                        errors.append(newFileName)
                    except Exception as e:
                        print("Error desconocido: {0}".format(e))
                        numFail += 1
                        errors.append(newFileName)

        if(numFail > 0):
            return Response({'message': 'fail', 'files_generated_ok': numOK, 'files_failed': numFail, 'errors': errors, 'ok': filesOK}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'ok', 'files_generated_ok': numOK, 'files_failed': numFail, 'errors': errors, 'ok': filesOK}, status=status.HTTP_201_CREATED)
