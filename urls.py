from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # serve sitemap at /sitemap.xml
    path(
        "sitemap.xml",
        TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml"),
        name="sitemap",
    ),
    # serve sitemap also at /sitemap (without .xml)
    path(
        "sitemap",
        TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml"),
        name="sitemap_noext",
    ),
    path('', include(('website.urls', 'website'), namespace='website')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
]
