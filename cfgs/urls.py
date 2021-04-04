from django.urls import path, include
# from . import views
from rest_framework import routers
from .views import PTsViewSet, DeviceTypeViewSet

router = routers.DefaultRouter()
router.register(r'pts', PTsViewSet)
router.register(r'types', DeviceTypeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
