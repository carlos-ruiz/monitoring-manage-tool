from rest_framework import serializers
from .models import PT, DeviceType, File


class PTSerializer(serializers.ModelSerializer):
    class Meta:
        model = PT
        fields = '__all__'


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
