from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
import json
import re
import os
import logging
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

logger = logging.getLogger(__name__)
from decimal import Decimal, InvalidOperation
from core.models import (
    Course, BlogPost, Testimonial, GalleryImage, 
    Application, AboutPage, ContactInfo, ContactMessage, AboutImage, AboutVideo
)
from core.models import Video
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
        'videos': Video.objects.filter(is_active=True).order_by('-created_at')[:6],
    }
    return render(request, 'website/index.html', context)


def videos(request):
    """Page that lists all videos"""
    videos_qs = Video.objects.filter(is_active=True).order_by('order', '-created_at')
    return render(request, 'website/videos.html', {'videos': videos_qs})


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
    gallery_images = course.images.filter(is_active=True).order_by('order', 'id')
    
    context = {
        'course': course,
        'related_courses': related_courses,
        'gallery_images': gallery_images,
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
        # Allow pre-selecting a listing via ?listing=<id>
        initial = {}
        listing_id = request.GET.get('listing')
        if listing_id:
            try:
                listing_obj = Course.objects.filter(pk=int(listing_id), is_active=True).first()
                if listing_obj:
                    initial['course'] = listing_obj
            except Exception:
                initial = {}
        form = ApplicationForm(initial=initial)
    
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
    # Allow pre-selecting a listing via ?listing=<id> or include listing in POST
    listing = None
    listing_id = request.GET.get('listing') or request.POST.get('listing')
    if listing_id:
        try:
            listing = Course.objects.filter(pk=int(listing_id), is_active=True).first()
        except Exception:
            listing = None

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Save message record; include listing title in subject if provided
            subj = cd.get('subject', '')
            if listing and not subj:
                subj = f'Inquiry about {listing.title}'

            cm = ContactMessage.objects.create(
                name=cd.get('name', ''),
                email=cd.get('email', ''),
                subject=subj,
                message=cd.get('message', ''),
                sent=False,
                attempts=0,
            )

            # Persist conversation for admin review
            try:
                from core.models import Conversation, ConversationMessage
                conv = Conversation.objects.create(
                    listing=listing,
                    name=cd.get('name', ''),
                    email=cd.get('email', ''),
                    subject=subj or f'Inquiry {listing.title if listing else ""}',
                )
                ConversationMessage.objects.create(
                    conversation=conv,
                    sender='visitor',
                    text=cd.get('message', ''),
                )
            except Exception:
                conv = None

            subject = cm.subject or 'Website contact'
            body = f"From: {cm.name or 'Anonymous'} <{cm.email or 'no-reply'}>\n\n"
            if listing:
                body += f"Listing: {listing.title} (ID: {listing.pk})\nLocation: {listing.location or 'N/A'}\nPrice: {listing.fees or 'N/A'}\nLink: {request.build_absolute_uri(listing.get_absolute_url() if hasattr(listing, 'get_absolute_url') else f'/course/{listing.pk}/')}\n\n"
            body += cm.message

            try:
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
        # Prefill subject if listing provided
        initial = {}
        if listing:
            initial['subject'] = f'Inquiry about {listing.title}'
            initial['message'] = ''
        form = ContactForm(initial=initial)

    return render(request, 'website/contact.html', {
        'form': form,
        'contact_info': contact_info,
        'listing': listing,
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


def landai_chat_api(request):
    """Simple backend endpoint to drive LandAI replies.
    This is a minimal placeholder that can be expanded to call an external AI provider.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    try:
        payload = json.loads(request.body.decode('utf-8'))
        message = payload.get('message', '').strip()
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    if not message:
        return JsonResponse({'reply': 'Please include a question or request.'})
    # At this point the code will compute `reply`, `listings`, and `suggestions` below.
    # Enhanced: intent detection + DB-backed listing results
    lower = message.lower()

    # Price/number extractor and helper to build listing dicts
    listings = []
    def course_to_dict(c):
        return {
            'id': c.pk,
            'title': c.title,
            'slug': c.slug,
            'location': c.location,
            'fees': str(c.fees) if c.fees is not None else None,
            'image': c.featured_image.url if getattr(c, 'featured_image', None) and hasattr(c.featured_image, 'url') else None,
            'excerpt': (c.extra_details[:200] + '...') if c.extra_details else '',
            'detail_url': f'/course/{c.pk}/',
            'apply_url': f'/apply/?listing={c.pk}',
        }

    # Helper: parse numeric KES amounts like '800000' or '800,000'
    def parse_amount(text):
        m = re.search(r'([0-9]+(?:[,\s][0-9]{3})*)', text)
        if not m:
            return None
        raw = m.group(1)
        cleaned = raw.replace(',', '').replace(' ', '')
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None

    # Build suggestions to help the user next
    suggestions = [
        'Show plots under KES 800000',
        'Land near Nakuru',
        'Installment plans',
        'Contact sales',
    ]

    try:
        # Prepare known locations from DB for fuzzy matching
        known_locations_qs = Course.objects.filter(is_active=True).values_list('location', flat=True)
        known_locations = [l.strip() for l in known_locations_qs if l and l.strip()]

        def fuzzy_match_location(text):
            if not text:
                return None
            t = text.lower().strip()
            # direct contains
            for loc in known_locations:
                if t == loc.lower() or t in loc.lower() or loc.lower() in t:
                    return loc
            # token overlap heuristic
            tokens = set(re.findall(r"[a-zA-Z]+", t))
            best = None
            best_score = 0
            for loc in known_locations:
                loc_tokens = set(re.findall(r"[a-zA-Z]+", loc.lower()))
                score = len(tokens & loc_tokens)
                if score > best_score:
                    best_score = score
                    best = loc
            if best_score >= 1:
                return best
            return None

        # If the user asks for cheaper items but no budget provided, ask a clarifying question
        if any(word in lower for word in ('cheaper', 'cheap', 'cheapest', 'what can i get', 'what can i get cheaper')):
            amt = parse_amount(lower)
            if not amt:
                reply = 'What is your maximum budget? For example: "Under KES 800000" — or pick a suggestion.'
                return JsonResponse({'reply': reply, 'suggestions': suggestions, 'listings': []})
            # otherwise fall through to price search

        # Price intent: 'under', 'below', 'less than', or explicit numeric amount
        if any(token in lower for token in ('under', 'below', 'less than')) or parse_amount(lower) is not None:
            cap = parse_amount(lower) or Decimal('800000')
            qs = Course.objects.filter(is_active=True, fees__isnull=False, fees__lte=cap)
            # rank by fees ascending
            qs = qs.order_by('fees')[:12]
            listings = [course_to_dict(c) for c in qs]
            if listings:
                # pick best representative
                first = listings[0]
                reply = f'I found {len(listings)} listings under KES {int(cap):,}. For example, "{first["title"]}" at KES {first["fees"]} in {first.get("location","unspecified")}. '
            else:
                reply = f'Sorry, I could not find listings under KES {int(cap):,}. Try increasing your budget or ask about locations.'

        # Location intent
        elif any(token in lower for token in ('near', 'in', 'around')) or any(city in lower for city in ('nakuru', 'nanyuki', 'nairobi')):
            loc_match = re.search(r'near\s+([a-zA-Z\s]+)|in\s+([a-zA-Z\s]+)|around\s+([a-zA-Z\s]+)', lower)
            loc = None
            if loc_match:
                loc = next((g for g in loc_match.groups() if g), None)
            if not loc:
                for city in ('nakuru', 'nanyuki', 'nairobi'):
                    if city in lower:
                        loc = city.capitalize()
                        break

            if not loc:
                reply = 'Which town or area are you interested in? (e.g., Nakuru, Nanyuki)'
                return JsonResponse({'reply': reply, 'suggestions': suggestions, 'listings': []})

            # try fuzzy matching against known locations
            matched = fuzzy_match_location(loc)
            if matched:
                qs = Course.objects.filter(is_active=True, location__icontains=matched).order_by('-created_at')[:12]
            else:
                qs = Course.objects.filter(is_active=True, location__icontains=loc).order_by('-created_at')[:12]
            listings = [course_to_dict(c) for c in qs]
            if listings:
                reply = f'I found {len(listings)} listings near {loc} — showing top results.'
            else:
                reply = f'Sorry, I could not find listings near {loc}. Try a nearby town or broaden your search.'

        # Payment/installment queries
        elif any(token in lower for token in ('installment', 'payment', 'plan', 'monthly')):
            reply = 'Installment plans: we offer 6, 12, 24 and 36 month options. Monthly payments depend on the plot price; tell me a budget and I can calculate an estimate.'

        # Booking/contact
        elif any(token in lower for token in ('book', 'call', 'contact', 'reserve')):
            reply = 'To book a call or reserve a plot, use the "Book a Call" button on any listing or visit the Contact page. Would you like contact details?'

        else:
            # If it's a straightforward question, answer directly; otherwise give helpful guidance
            if lower.strip().endswith('?') or lower.split()[0] in ('what', 'which', 'how', 'where', 'can', 'could'):
                reply = ('Good question — I can search listings, explain fees and plans, or help book viewings. '
                         'Try: "Show plots under KES 800000" or "Land near Nakuru". If you prefer, tell me your budget and preferred town.')
            else:
                reply = ('Hi — I can find listings, compare locations, explain payment plans, or help book a viewing. '
                         'Try: "Show plots under KES 800000" or "Land near Nakuru".')

    except Exception:
        reply = 'Sorry, something went wrong while searching. Please try again.'

    # If we have an OpenAI key and the OpenAI client is available, call OpenAI
    api_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
    if api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=api_key)
            # Provide a short JSON summary of up to 6 listings to ground the model
            ground = json.dumps(listings[:6], ensure_ascii=False)
            system_msg = (
                "You are a concise real-estate assistant. Use the provided JSON 'listings' to answer user queries. "
                "If the answer requires exact price or availability, prefer the provided listings and avoid fabricating details. "
                "When appropriate, suggest actions: view, book, contact sales. Keep replies short (1-3 sentences)."
            )
            user_msg = f"User question: {message}\n\nContext listings JSON (may be empty):\n{ground}"
            resp = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=400,
                temperature=0.1,
            )
            # New client returns objects with attributes
            ai_reply = None
            try:
                ai_reply = resp.choices[0].message.content
            except Exception:
                # Fallback to dict-style indexing if necessary
                try:
                    ai_reply = resp['choices'][0]['message']['content']
                except Exception:
                    ai_reply = None

            if ai_reply:
                return JsonResponse({'reply': ai_reply, 'listings': listings, 'suggestions': suggestions})
        except Exception:
            # If OpenAI fails, log the exception and fall back to local reply
            try:
                logger.exception('OpenAI request failed')
            except Exception:
                pass
            pass

    return JsonResponse({'reply': reply, 'listings': listings, 'suggestions': suggestions})


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
