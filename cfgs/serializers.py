from rest_framework import serializers
from .models import PT


class PTSerializer(serializers.ModelSerializer):
    class Meta:
        model = PT
        fields = '__all__'
