from rest_framework import serializers
from .models import PT, DeviceType


class PTSerializer(serializers.ModelSerializer):
    class Meta:
        model = PT
        fields = '__all__'


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'
