from rest_framework import viewsets
from appointments.models import Appointment
from authentication.models import User
from .serializers import AppointmentSerializer, UserSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer