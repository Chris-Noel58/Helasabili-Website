from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    
    # Dashboard home
    path('', views.dashboard_home, name='dashboard'),
    
    # Courses
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/add/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Blog
    path('posts/', views.blog_list, name='blog_list'),
    path('posts/add/', views.blog_create, name='blog_create'),
    path('posts/<int:pk>/edit/', views.blog_update, name='blog_update'),
    path('posts/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    
    # Testimonials
    path('testimonials/', views.testimonials_list, name='testimonials_list'),
    path('testimonials/add/', views.testimonial_create, name='testimonial_create'),
    # plural alias for templates that use 'testimonials_create'
    path('testimonials/add/', views.testimonial_create, name='testimonials_create'),
    path('testimonials/<int:pk>/edit/', views.testimonial_update, name='testimonial_update'),
    # plural alias for templates that use 'testimonials_update'
    path('testimonials/<int:pk>/edit/', views.testimonial_update, name='testimonials_update'),
    path('testimonials/<int:pk>/delete/', views.testimonial_delete, name='testimonial_delete'),
    # plural alias for templates that use 'testimonials_delete'
    path('testimonials/<int:pk>/delete/', views.testimonial_delete, name='testimonials_delete'),

    # Gallery
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/add/', views.gallery_upload, name='gallery_upload'),
    path('gallery/<int:pk>/edit/', views.gallery_update, name='gallery_update'),
    path('gallery/<int:pk>/delete/', views.gallery_delete, name='gallery_delete'),
    
    # Applications
    path('applications/', views.applications_list, name='applications_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/export/', views.applications_export_csv, name='applications_export_csv'),
    
    # About & Contact
    path('about/edit/', views.about_page_edit, name='about_page_edit'),
    path('contact/edit/', views.contact_info_edit, name='contact_info_edit'),
    path('contact/list/', views.contact_list, name='contact_list'),
    path('contact/form/', views.contact_edit, name='contact_edit'),
    # Add aliases so templates can link to adding contact info
    path('contact/add/', views.contact_info_edit, name='contact_add'),
    path('contacti/add/', views.contact_info_edit, name='contact_create'),
]
