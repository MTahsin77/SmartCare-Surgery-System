from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('unauthorized/', views.unauthorized_access, name='unauthorized_access'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('list/', views.list_appointments, name='list_appointments'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('nurse-dashboard/', views.nurse_dashboard, name='nurse_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
