from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.core.paginator import Paginator
from core.models import (
    Course, BlogPost, Testimonial, GalleryImage,
    Application, AboutPage, ContactInfo, AdminProfile
)
from core.forms import (
    CourseForm, BlogPostForm, TestimonialForm, GalleryImageForm,
    AboutPageForm, ContactInfoForm, AdminLoginForm, ContactForm
)
from django.contrib.auth.models import User
from website.views import get_client_ip
import csv
from datetime import datetime
from django.template import TemplateDoesNotExist


# ===================== AUTHENTICATION =====================

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


def admin_login_view(request):
    """Admin login view"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and is_admin(user):
                login(request, user)
                # Update login IP
                admin_profile, _ = AdminProfile.objects.get_or_create(user=user)
                admin_profile.last_login_ip = get_client_ip(request)
                admin_profile.save()
                
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions')
    else:
        form = AdminLoginForm()
    
    return render(request, 'dashboard/login.html', {'form': form})


def admin_logout_view(request):
    """Admin logout view"""
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('dashboard:login')


# ===================== DASHBOARD HOME =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def dashboard_home(request):
    """Dashboard home view with statistics"""
    context = {
        'total_applications': Application.objects.count(),
        'total_courses': Course.objects.count(),
        'total_posts': BlogPost.objects.count(),
        'total_gallery': GalleryImage.objects.count(),
        'total_testimonials': Testimonial.objects.count(),
        'new_applications': Application.objects.filter(status='new').count(),
        'recent_applications': Application.objects.all()[:5],
        'recent_posts': BlogPost.objects.all()[:5],
        'applications_by_course': Application.objects.values('course__title').annotate(count=Count('id'))[:5],
        'applications_by_status': Application.objects.values('status').annotate(count=Count('id')),
    }
    return render(request, 'dashboard/index.html', context)


# ===================== COURSES MANAGEMENT =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def courses_list(request):
    """List all courses"""
    courses = Course.objects.all().order_by('order', 'title')
    search = request.GET.get('search', '')
    if search:
        courses = courses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    paginator = Paginator(courses, 10)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    return render(request, 'dashboard/courses/list.html', {
        'courses': courses,
        'search_query': search
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def course_create(request):
    """Create new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('dashboard:courses_list')
    else:
        form = CourseForm()
    
    return render(request, 'dashboard/courses/form.html', {
        'form': form,
        'title': 'Add New Course'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def course_update(request, pk):
    """Update course"""
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('dashboard:courses_list')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'dashboard/courses/form.html', {
        'form': form,
        'course': course,
        'title': f'Edit - {course.title}'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def course_delete(request, pk):
    """Delete course"""
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, 'Course deleted successfully!')
    return redirect('dashboard:courses_list')


# ===================== BLOG POSTS MANAGEMENT =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def blog_list(request):
    """List all blog posts"""
    posts = BlogPost.objects.all().order_by('-published_date')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    if status:
        posts = posts.filter(status=status)
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'dashboard/blog/list.html', {
        'posts': posts,
        'search_query': search,
        'filter_status': status
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def blog_create(request):
    """Create new blog post"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.get_full_name() or request.user.username
            post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('dashboard:blog_list')
    else:
        form = BlogPostForm()
    
    return render(request, 'dashboard/blog/form.html', {
        'form': form,
        'title': 'Add New Blog Post'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def blog_update(request, pk):
    """Update blog post"""
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('dashboard:blog_list')
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'dashboard/blog/form.html', {
        'form': form,
        'post': post,
        'title': f'Edit - {post.title}'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def blog_delete(request, pk):
    """Delete blog post"""
    post = get_object_or_404(BlogPost, pk=pk)
    post.delete()
    messages.success(request, 'Blog post deleted successfully!')
    return redirect('dashboard:blog_list')


# ===================== TESTIMONIALS MANAGEMENT =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def testimonials_list(request):
    """List all testimonials"""
    testimonials = Testimonial.objects.all().order_by('order', '-created_at')
    search = request.GET.get('search', '')
    
    if search:
        testimonials = testimonials.filter(
            Q(name__icontains=search) |
            Q(course__icontains=search)
        )
    
    paginator = Paginator(testimonials, 10)
    page = request.GET.get('page')
    testimonials = paginator.get_page(page)
    
    return render(request, 'dashboard/testimonials/list.html', {
        'testimonials': testimonials,
        'search_query': search
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def testimonial_create(request):
    """Create new testimonial"""
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial added successfully!')
            return redirect('dashboard:testimonials_list')
    else:
        form = TestimonialForm()
    
    return render(request, 'dashboard/testimonials/form.html', {
        'form': form,
        'title': 'Add New Testimonial'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def testimonial_update(request, pk):
    """Update testimonial"""
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial updated successfully!')
            return redirect('dashboard:testimonials_list')
    else:
        form = TestimonialForm(instance=testimonial)
    
    return render(request, 'dashboard/testimonials/form.html', {
        'form': form,
        'testimonial': testimonial,
        'title': f'Edit - {testimonial.name}'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def testimonial_delete(request, pk):
    """Delete testimonial"""
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.delete()
    messages.success(request, 'Testimonial deleted successfully!')
    return redirect('dashboard:testimonials_list')


# ===================== GALLERY MANAGEMENT =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def gallery_list(request):
    """List all gallery images"""
    images = GalleryImage.objects.all().order_by('category', 'order')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    if search:
        images = images.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    if category:
        images = images.filter(category=category)
    
    paginator = Paginator(images, 15)
    page = request.GET.get('page')
    images = paginator.get_page(page)
    
    return render(request, 'dashboard/gallery/list.html', {
        'images': images,
        'categories': GalleryImage.CATEGORY_CHOICES,
        'filter_category': category,
        'search_query': search
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def gallery_upload(request):
    """Upload new gallery image"""
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect('dashboard:gallery_list')
    else:
        form = GalleryImageForm()
    
    return render(request, 'dashboard/gallery/form.html', {
        'form': form,
        'title': 'Upload New Image'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def gallery_update(request, pk):
    """Update gallery image"""
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image updated successfully!')
            return redirect('dashboard:gallery_list')
    else:
        form = GalleryImageForm(instance=image)
    
    return render(request, 'dashboard/gallery/form.html', {
        'form': form,
        'image': image,
        'title': f'Edit - {image.title}'
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def gallery_delete(request, pk):
    """Delete gallery image"""
    image = get_object_or_404(GalleryImage, pk=pk)
    image.delete()
    messages.success(request, 'Image deleted successfully!')
    return redirect('dashboard:gallery_list')


# ===================== APPLICATIONS MANAGEMENT =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def applications_list(request):
    """List all applications"""
    applications = Application.objects.all().order_by('-created_at')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    course = request.GET.get('course', '')
    
    if search:
        applications = applications.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    if status:
        applications = applications.filter(status=status)
    if course:
        applications = applications.filter(course_id=course)
    
    paginator = Paginator(applications, 20)
    page = request.GET.get('page')
    applications = paginator.get_page(page)
    
    return render(request, 'dashboard/applications/list.html', {
        'applications': applications,
        'courses': Course.objects.all(),
        'statuses': Application.STATUS_CHOICES,
        'search_query': search,
        'filter_status': status,
        'filter_course': course
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def application_detail(request, pk):
    """View application details"""
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f'Application status updated to {new_status}!')
    
    return render(request, 'dashboard/applications/detail.html', {
        'application': application,
        'statuses': Application.STATUS_CHOICES
    })


@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def applications_export_csv(request):
    """Export applications to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applications.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Email', 'Phone', 'Course', 'Status', 'Date Applied'])
    
    applications = Application.objects.all().values_list(
        'full_name', 'email', 'phone', 'course__title', 'status', 'created_at'
    )
    for app in applications:
        writer.writerow(app)
    
    return response


# ===================== ABOUT PAGE MANAGEMENT =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def about_page_edit(request):
    """Edit about page"""
    about = AboutPage.objects.first()
    if not about:
        about = AboutPage.objects.create()
    
    if request.method == 'POST':
        form = AboutPageForm(request.POST, request.FILES, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, 'About page updated successfully!')
            return redirect('dashboard:about_page_edit')
    else:
        form = AboutPageForm(instance=about)
    
    return render(request, 'dashboard/about/form.html', {
        'form': form,
        'title': 'Edit About Page'
    })


# ===================== CONTACT INFO MANAGEMENT =====================

@login_required(login_url='dashboard:login')
@user_passes_test(is_admin)
def contact_info_edit(request):
    """Edit contact information"""
    contact = ContactInfo.objects.first()
    if not contact:
        contact = ContactInfo.objects.create(
            phone_primary='+254 (0) 123 456 789',
            email='info@nchskikuyu.ac.ke'
        )
    
    if request.method == 'POST':
        form = ContactInfoForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact information updated successfully!')
            return redirect('dashboard:contact_info_edit')
    else:
        form = ContactInfoForm(instance=contact)
    
    return render(request, 'dashboard/contact/form.html', {
        'form': form,
        'title': 'Edit Contact Information'
    })


# Ensure contact views render the correct templates
def contact_list(request):
    try:
        contact_info = ContactInfo.objects.first()
    except Exception:
        contact_info = None
    return render(request, 'dashboard/contact/list.html', {'contact_info': contact_info})


def contact_edit(request):
    try:
        contact_info = ContactInfo.objects.first()
    except Exception:
        contact_info = None

    if request.method == 'POST':
        # Use the ContactForm for validation
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if contact_info:
                contact_info.phone_primary = data.get('phone_primary', contact_info.phone_primary)
                contact_info.email = data.get('email', contact_info.email)
                contact_info.address = data.get('message', contact_info.address)
                contact_info.save()
            else:
                ContactInfo.objects.create(
                    phone_primary=data.get('phone_primary', ''),
                    email=data.get('email', ''),
                    address=data.get('message', ''),
                    postal_code='', city='', country='Kenya'
                )
            messages.success(request, 'Contact information updated')
            return redirect('dashboard:contact_list')
    else:
        # Pre-fill form if contact info exists
        if contact_info:
            initial = {
                'email': contact_info.email,
                'name': '',
                'subject': '',
                'message': contact_info.address,
            }
            form = ContactForm(initial=initial)
        else:
            form = ContactForm()

    try:
        return render(request, 'dashboard/contact/form.html', {'form': form, 'contact_info': contact_info})
    except TemplateDoesNotExist:
        # Fallback: render a minimal inline response to avoid TemplateDoesNotExist
        from django.http import HttpResponse
        return HttpResponse('Contact edit form template not found. Please ensure templates/dashboard/contact/form.html exists.', status=500)


# Testimonials views
def testimonials_list(request):
    testimonials = Testimonial.objects.order_by('order', '-created_at')
    try:
        return render(request, 'dashboard/testimonials/list.html', {'testimonials': testimonials})
    except TemplateDoesNotExist:
        from django.http import HttpResponse
        return HttpResponse('Testimonials list template missing.', status=500)


def testimonials_create(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial created')
            return redirect('dashboard:testimonials')
    else:
        form = TestimonialForm()
    try:
        return render(request, 'dashboard/testimonials/form.html', {'form': form})
    except TemplateDoesNotExist:
        from django.http import HttpResponse
        return HttpResponse('Testimonials form template missing.', status=500)


def testimonials_edit(request, pk):
    obj = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial updated')
            return redirect('dashboard:testimonials')
    else:
        form = TestimonialForm(instance=obj)
    try:
        return render(request, 'dashboard/testimonials/form.html', {'form': form})
    except TemplateDoesNotExist:
        from django.http import HttpResponse
        return HttpResponse('Testimonials form template missing.', status=500)


def testimonials_delete(request, pk):
    obj = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Testimonial deleted')
        return redirect('dashboard:testimonials')
    try:
        return render(request, 'dashboard/testimonials/confirm_delete.html', {'object': obj})
    except TemplateDoesNotExist:
        from django.http import HttpResponse
        return HttpResponse('Confirm delete template missing.', status=500)
