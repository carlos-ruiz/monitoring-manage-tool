from django.urls import path, include
# from . import views
from rest_framework import routers
from .views import PTsViewSet, DeviceTypeViewSet, CFGsViewSet

router = routers.DefaultRouter()
router.register(r'pts', PTsViewSet)
router.register(r'types', DeviceTypeViewSet)
router.register(r'cfgs', CFGsViewSet, basename='cfgs')

urlpatterns = [
    path('', include(router.urls))
]
