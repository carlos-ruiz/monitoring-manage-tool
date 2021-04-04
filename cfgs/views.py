from django.shortcuts import render
from django.http import HttpResponse
from .models import PT
from rest_framework import viewsets
from .serializers import PTSerializer

# Create your views here.


def index(request):
    return HttpResponse("Hello world!")


def home(request):
    all_pts = PT.objects.all()
    context = {'all_pts': all_pts}
    return render(request, 'cfgs/index.html', context)


class PTsViewSet(viewsets.ModelViewSet):
    queryset = PT.objects.all()
    serializer_class = PTSerializer
