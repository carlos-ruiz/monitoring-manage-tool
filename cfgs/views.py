from django.http import HttpResponse
from .models import PT, DeviceType, File, CFG
from rest_framework import viewsets
from .serializers import PTSerializer, DeviceTypeSerializer, FileSerializer, CFGSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import csv
from PITA.settings import BASE_DIR
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import shutil
import os
import json
import zipfile
from datetime import date
import shlex
import subprocess
from .SSHConnection import SSHConnection
import logging

# Create your endpoints here.

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', filename='messages.log',
                    encoding='utf-8', level=logging.DEBUG)


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
    elif templateType == 'esx':
        template = 'SVR-ESX.cfg'
    elif templateType == 'ap':
        template = 'AP.cfg'
    elif templateType == 'planet':
        template = 'PLANET.cfg'

    return template


def zip_cfgs(source_path):
    zip_path = "{0}cfgs_{1}.zip".format(
        str(BASE_DIR)+'/cfgs/generated/', date.today().strftime("%d_%m_%Y"))
    zf = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    src = os.path.abspath(source_path)
    for dirname, subdirs, files in os.walk(source_path):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(src) + 1:]
            logging.info('zipping %s as %s' %
                         (os.path.join(dirname, filename), arcname))
            zf.write(absname, arcname)
    zf.close()
    return zip_path


def validateUploads(ipnagios):
    sshConnection = SSHConnection()
    con = sshConnection.getConnection(ipnagios)

    stdin, stdout, stderr = con.exec_command(
        '/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg | grep Errors: | awk \'{print $3}\'')
    # process the output
    if stderr.read() == b'':
        for line in stdout.readlines():
            errors = line.strip()
            logging.info("Errors: %s" % errors)
            # if errors == '0':
            # stdin, stdout, stderr = con.exec_command(
            #     'service nagios restart')
            # print(stdout.readlines())

    else:
        logging.error(stderr.read())
    con.close()


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
                        device_type=line[0], nagiosDeviceHostgroup=line[1])
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

    @action(detail=False, methods=['post'], name='Download zip')
    def download_cfgs(self, request, *args, **kwargs):
        source_path = request.data.get('path')
        logging.debug("CFGs Path: {0}".format(source_path))
        zip_path = zip_cfgs(source_path)
        logging.debug("Path zip: {0}".format(zip_path))
        zip_file = open(zip_path, 'rb')
        response = HttpResponse(
            zip_file, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="%s"' % 'cfgs.zip'
        return response

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
        try:
            if(os.path.isdir(generatedPath)):
                shutil.rmtree(generatedPath)
            os.mkdir(generatedPath)
        except:
            logging.error(
                "Error al borrar el folder: {0}".format(generatedPath))

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
                    logging.error(
                        "No se encontró la plantilla para este tipo de equipo")
                    numFail += 1
                    errors.append(newFileName)
                    continue

                try:
                    with open(template) as tc:
                        t = tc.read()
                except:
                    logging.error(
                        "No se puede leer la plantilla {0}".format(template))
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
                        vpn = PT.objects.get(pk=line[0])
                        hostgroup = DeviceType.objects.get(device_type=line[3])
                        cfg = CFG(folder=generatedPath, file=newFileName,
                                  hostgroup=hostgroup, vpn=vpn, uploaded=False)
                        cfg.save()
                    except IOError as e:
                        logging.error("Error al escribir el archivo %s" % e)
                        numFail += 1
                        errors.append(newFileName)
                    except Exception as e:
                        logging.error("Error desconocido: {0}".format(e))
                        numFail += 1
                        errors.append(newFileName)

        if(numFail > 0):
            return Response({'message': 'fail', 'files_generated_ok': numOK, 'files_failed': numFail, 'errors': errors, 'ok': filesOK, 'path': generatedPath}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'ok', 'files_generated_ok': numOK, 'files_failed': numFail, 'errors': errors, 'ok': filesOK, 'path': generatedPath}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], name='Deploy to remotes nagios')
    def deploy(self, request, *args, **kwargs):
        cfgsPath = request.data['path']
        logging.info("CFGs path: "+cfgsPath)
        cfgs = CFG.objects.filter(folder=cfgsPath).order_by(
            'vpn', 'hostgroup__nagiosDeviceHostgroup')
        filesUploaded = []
        filesError = []

        filesToUpload = {}
        for cfgFile in cfgs:
            vpn = cfgFile.vpn.vpn
            hostgroup = cfgFile.hostgroup.nagiosDeviceHostgroup

            if vpn in filesToUpload:
                if hostgroup in filesToUpload[vpn]:
                    filesToUpload[vpn][hostgroup] += ' ' + \
                        str(cfgsPath)+cfgFile.file
                else:
                    filesToUpload[vpn][hostgroup] = str(cfgsPath)+cfgFile.file
            else:
                filesToUpload.update(
                    {vpn: {hostgroup: str(cfgsPath)+cfgFile.file, "ip": cfgFile.vpn.nagios_ip}})

        for vpn in filesToUpload:
            ip = filesToUpload[vpn].pop('ip')

            for hostgroup in filesToUpload[vpn]:
                files = filesToUpload[vpn][hostgroup]
                try:
                    create_folder = "mkdir -p /tmp/components/{hostgroup}".format(
                        hostgroup=hostgroup)
                    sshConnection = SSHConnection().getConnection(ip)
                    sshConnection.exec_command(create_folder)
                    sshConnection.close()
                    command_line = "scp {files} root@{nagiosIP}:/tmp/components/{hostgroup}/".format(
                        files=files, nagiosIP=ip, hostgroup=hostgroup)
                    args = shlex.split(command_line)
                    subprocess.Popen(
                        args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                    cfgs = files.split(' ')
                    filesNames = ''
                    for cfg in cfgs:
                        lastSlash = cfg.rfind('/')
                        fileName = cfg[lastSlash+1:]
                        filesUploaded.append(fileName)
                        cfgFile = CFG.objects.get(
                            folder=cfgsPath, file=fileName)
                        cfgFile.uploaded = True
                        cfgFile.save()
                        filesNames += ' '+fileName
                    logging.info("Uploaded {files} to {hostgroup} in {vpn}({ip})".format(
                        files=filesNames, hostgroup=hostgroup, vpn=vpn, ip=ip))
                except Exception as e:
                    cfgs = files.split(' ')
                    filesNames = ''
                    for cfg in cfgs:
                        lastSlash = cfg.rfind('/')
                        filesError.append(cfg[lastSlash+1:])
                        filesNames += ' '+cfg[lastSlash+1:]
                    logging.error("Error uploading {0} to {1} in server {2} PT {3}".format(
                        filesNames, hostgroup, ip, vpn))
                    logging.error(e)
                    continue
            validateUploads(ip)

        return Response({'message': 'Files uploaded', 'files_uploaded_ok': len(filesUploaded), 'files_failed': len(filesError), 'errors': filesError, 'ok': filesUploaded}, status=status.HTTP_200_OK)
