from django.urls import path
from django.views.generic import TemplateView, RedirectView
from . import views

app_name = 'website'

urlpatterns = [
    # Public website routes
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', RedirectView.as_view(url='/listings/', permanent=False), name='legacy_courses_redirect'),
    path('listings/', views.courses_list, name='courses_list'),
    path('course/<int:pk>/', views.course_detail, name='courses_detail'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('apply/', views.apply, name='apply'),
    path('contact/', views.contact, name='contact'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    # Sitemap routes
    path(
        "sitemap.xml",
        TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml"),
        name="sitemap",
    ),
    path(
        "sitemap",
        TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml"),
        name="sitemap_noext",
    ),
    path('student-portal/', views.student_portal, name='student_portal'),
    # Chat API for LandAI
    path('api/landai/chat/', views.landai_chat_api, name='landai_chat_api'),
    path('videos/', views.videos, name='videos'),
]
