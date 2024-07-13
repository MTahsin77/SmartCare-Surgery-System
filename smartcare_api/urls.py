from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, UserViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]