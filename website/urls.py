from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import RedirectView
from . import views
from .sitemaps import sitemaps

app_name = 'website'

urlpatterns = [
    # Public website routes
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', RedirectView.as_view(url='/listings/', permanent=False), name='legacy_courses_redirect'),
    path('listings/', views.courses_list, name='courses_list'),
    path('listings/<int:pk>/', views.course_detail, name='courses_detail'),
    path('course/<int:pk>/', RedirectView.as_view(pattern_name='website:courses_detail', permanent=False), name='legacy_course_detail_redirect'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('apply/', views.apply, name='apply'),
    path('site-visit-bookings/', views.site_visit_booking, name='site_visit_booking'),
    path('contact/', views.contact, name='contact'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    # SEO: dynamic sitemap (pages, listings, blog posts) and robots.txt
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('sitemap', RedirectView.as_view(url='/sitemap.xml', permanent=True), name='sitemap_noext'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    # Leftover from the original school template: send old links home
    path('student-portal/', RedirectView.as_view(url='/', permanent=True)),
    # Chat API for LandAI
    path('api/landai/chat/', views.landai_chat_api, name='landai_chat_api'),
    path('videos/', views.videos, name='videos'),
]
