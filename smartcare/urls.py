from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/', include('smartcare_api.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('appointments/', include('appointments.urls')),
    path('dashboards/', include('dashboards.urls')),
    path('collaboration/', include('collaboration.urls')),
    path('', include('home.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)