from django.urls import path, include
# from . import views
from rest_framework import routers
from .views import PTsViewSet

router = routers.DefaultRouter()
router.register(r'cfgs', PTsViewSet)

urlpatterns = [
    # path('', views.index, name='index'),
    # path('home', views.home, name='home')
    path('', include(router.urls))
]
