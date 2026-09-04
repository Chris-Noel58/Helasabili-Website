from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Dashboard
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    
    # Website
    path('', include(('website.urls', 'website'), namespace='website')),
]

# Serve media and static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'website.views.page_not_found'
handler500 = 'website.views.server_error'
