from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('unauthorized/', views.unauthorized_access, name='unauthorized_access'),
    path('gps/', views.gp_list, name='gp_list'),
    path('manage_gp/', views.manage_gp, name='manage_gps'),
    path('manage_gp/<int:gp_id>/', views.manage_gp, name='edit_gp'),
    path('delete_gp/<int:gp_id>/', views.delete_gp, name='delete_gp'),
    path('pending-registrations/', views.pending_registrations, name='pending_registrations'),
    path('approve-registration/<int:pending_id>/', views.approve_registration, name='approve_registration'),
]
