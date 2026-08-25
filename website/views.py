from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.conf import settings
from core.models import (
    Course, BlogPost, Testimonial, GalleryImage, 
    Application, AboutPage, ContactInfo, ContactMessage, AboutImage, AboutVideo
)
from core.forms import ApplicationForm, ContactForm
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import modelform_factory
from django.db import DatabaseError


# ==================== HOME & GENERAL PAGES ====================

def home(request):
    """Home page view with featured content"""
    courses = Course.objects.filter(is_active=True).order_by('order')[:3]
    testimonials = Testimonial.objects.filter(is_active=True).order_by('order')[:3]
    blog_posts = BlogPost.objects.filter(status='published').order_by('-published_date')[:3]
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('order')[:6]
    
    context = {
        'courses': courses,
        'testimonials': testimonials,
        'blog_posts': blog_posts,
        'gallery_images': gallery_images,
    }
    return render(request, 'website/index.html', context)


def about(request):
    """About page view"""
    try:
        about_page = AboutPage.objects.first()
    except AboutPage.DoesNotExist:
        about_page = None

    # Safely fetch related media; if migrations haven't been applied the related tables may not exist.
    about_images = []
    about_videos = []
    if about_page:
        try:
            about_images = list(about_page.images.all())
        except DatabaseError:
            about_images = []
        try:
            about_videos = list(about_page.videos.all())
        except DatabaseError:
            about_videos = []

    context = {
        'about': about_page,
        'about_images': about_images,
        'about_videos': about_videos,
    }
    return render(request, 'website/about.html', context)


# ==================== COURSES ====================

def courses_list(request):
    """List all courses with search"""
    courses = Course.objects.filter(is_active=True).order_by('order')
    search_query = request.GET.get('search', '')
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'courses': page_obj.object_list,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'website/courses.html', context)


def course_detail(request, pk):
    """Course detail view"""
    course = get_object_or_404(Course, pk=pk, is_active=True)
    related_courses = Course.objects.filter(is_active=True).exclude(pk=pk)[:3]
    
    context = {
        'course': course,
        'related_courses': related_courses,
    }
    return render(request, 'website/course_detail.html', context)


# ==================== BLOG ====================

def blog_list(request):
    """List all blog posts"""
    posts = BlogPost.objects.filter(status='published').order_by('-published_date')
    search_query = request.GET.get('search', '')
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Get featured post
    try:
        featured_post = BlogPost.objects.filter(status='published', is_featured=True).latest('published_date')
    except BlogPost.DoesNotExist:
        featured_post = None
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'featured_post': featured_post,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'website/blog.html', context)


def blog_detail(request, slug):
    """Blog post detail view"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment views
    post.views += 1
    post.save(update_fields=['views'])
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(pk=post.pk).order_by('-published_date')[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'website/blog_detail.html', context)


# ==================== GALLERY ====================

def gallery(request):
    """Gallery view"""
    images = GalleryImage.objects.filter(is_active=True).order_by('order')
    category = request.GET.get('category', '')
    
    if category:
        images = images.filter(category=category)
    
    # Pagination
    paginator = Paginator(images, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categories = GalleryImage.CATEGORY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'images': page_obj.object_list,
        'categories': categories,
        'selected_category': category,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'website/gallery.html', context)


# ==================== TESTIMONIALS ====================

def testimonials(request):
    """Testimonials view"""
    testimonials_list = Testimonial.objects.filter(is_active=True).order_by('order')
    
    # Pagination
    paginator = Paginator(testimonials_list, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'testimonials': page_obj.object_list,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'website/testimonials.html', context)


# ==================== APPLICATION ====================

@require_http_methods(["GET", "POST"])
def apply(request):
    """Application form view"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.ip_address = get_client_ip(request)
            application.save()
            
            messages.success(request, 'Application submitted successfully! We will contact you soon.')
            return redirect('website:home')
    else:
        form = ApplicationForm()
    
    courses = Course.objects.filter(is_active=True)
    
    try:
        contact_info = ContactInfo.objects.first()
    except ContactInfo.DoesNotExist:
        contact_info = None
    
    context = {
        'form': form,
        'courses': courses,
        'contact_info': contact_info,
    }
    return render(request, 'website/apply.html', context)


# ==================== CONTACT ====================

@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact page view"""
    contact_info = None
    try:
        contact_info = ContactInfo.objects.first()
    except ContactInfo.DoesNotExist:
        contact_info = None

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Save message record
            cm = ContactMessage.objects.create(
                name=cd.get('name', ''),
                email=cd.get('email', ''),
                subject=cd.get('subject', ''),
                message=cd.get('message', ''),
                sent=False,
                attempts=0,
            )

            subject = cm.subject or 'Website contact'
            body = f"From: {cm.name or 'Anonymous'} <{cm.email or 'no-reply'}>\n\n{cm.message}"

            try:
                # Use the visitor's email/address in the From header when provided.
                # NOTE: many SMTP providers (Gmail) require the envelope sender to match the authenticated account;
                # sending with an arbitrary From may be rejected or rewritten by the SMTP server. If that happens,
                # the exception will be recorded in ContactMessage.
                from_email = f"{cm.name} <{cm.email}>" if cm.email else settings.DEFAULT_FROM_EMAIL
                headers = {'Reply-To': cm.email} if cm.email else None

                email = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=from_email,
                    to=[settings.DEFAULT_FROM_EMAIL],
                    reply_to=[cm.email] if cm.email else None,
                    headers=headers,
                )
                email.send(fail_silently=False)

                cm.sent = True
                cm.attempts += 1
                cm.last_error = ''
                cm.save()
                messages.success(request, 'Your message has been sent. We will contact you shortly.')
            except Exception as e:
                cm.attempts += 1
                cm.last_error = str(e)
                cm.save()
                messages.error(request, 'There was a problem sending your message. The message has been saved and we will retry.')
            return redirect('website:contact')
    else:
        form = ContactForm()

    return render(request, 'website/contact.html', {
        'form': form,
        'contact_info': contact_info,
    })


# ==================== NEWSLETTER ====================

@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Newsletter subscription"""
    email = request.POST.get('email', '')
    
    if email:
        # Handle newsletter subscription
        messages.success(request, 'Successfully subscribed to our newsletter!')
    else:
        messages.error(request, 'Please enter a valid email address.')
    
    return redirect(request.META.get('HTTP_REFERER', 'website:home'))


# ==================== ADMIN VIEWS ====================

@staff_member_required
def about_admin_edit(request):
    """Admin view to edit AboutPage and manage media uploads/deletions"""
    AboutForm = modelform_factory(AboutPage, exclude=())
    about = AboutPage.objects.first()
    if request.method == 'POST':
        form = AboutForm(request.POST, request.FILES, instance=about)
        if form.is_valid():
            about = form.save()

            # Handle deletions (checkboxes send single values; convert to lists)
            delete_image_ids = request.POST.getlist('delete_images')
            delete_video_ids = request.POST.getlist('delete_videos')
            if delete_image_ids:
                AboutImage.objects.filter(id__in=delete_image_ids, about=about).delete()
            if delete_video_ids:
                AboutVideo.objects.filter(id__in=delete_video_ids, about=about).delete()

            # Handle uploaded images
            images = request.FILES.getlist('images')
            for f in images:
                AboutImage.objects.create(about=about, image=f)

            # Handle uploaded videos
            videos = request.FILES.getlist('videos')
            for f in videos:
                AboutVideo.objects.create(about=about, file=f)

            messages.success(request, 'About page updated successfully.')
            return redirect('dashboard:about_edit')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = AboutForm(instance=about)

    context = {
        'form': form,
        'about': about,
    }
    return render(request, 'dashboard/about/form.html', context)


# ==================== STUDENT PORTAL ====================

def student_portal(request):
    """Render the student portal template"""
    return render(request, 'website/student_portal.html')


# ==================== UTILITY FUNCTIONS ====================

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==================== ERROR HANDLERS ====================

def page_not_found(request, exception):
    """Custom 404 handler"""
    try:
        return render(request, 'errors/404.html', status=404)
    except Exception:
        # Fallback simple response if template missing
        from django.http import HttpResponse
        return HttpResponse('Page not found', status=404)


def server_error(request):
    """Custom 500 handler"""
    try:
        return render(request, 'errors/500.html', status=500)
    except Exception:
        from django.http import HttpResponse
        return HttpResponse('Server error', status=500)
