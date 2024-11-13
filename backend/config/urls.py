from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),  # Include all user app URLs
    path('api/courses/', include('apps.courses.urls')),
    # path('api/calendar/', include('apps.calendar.urls')),
    path('media/', serve, {'document_root': settings.MEDIA_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)