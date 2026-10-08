from django.db import models
from django.core.validators import URLValidator, EmailValidator
from django.utils.text import slugify
from PIL import Image, ImageOps
import os
from django.utils import timezone
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage


def _stored_image_name(instance, field_name):
    if not instance.pk:
        return None
    return type(instance).objects.filter(pk=instance.pk).values_list(field_name, flat=True).first()


def _optimize_image(image_field, previous_name, max_size):
    if not image_field or image_field.name == previous_name:
        return

    _normalize_image_file(image_field, max_size)


def _normalize_image_file(image_field, max_size):
    """Apply EXIF rotation and size limits to an image stored on local disk."""
    image_path = image_field.path
    if not os.path.exists(image_path):
        return False

    with Image.open(image_path) as source:
        image_format = source.format
        orientation = source.getexif().get(274, 1)
        image = ImageOps.exif_transpose(source).copy()
        icc_profile = source.info.get('icc_profile')

    if image_format not in {'JPEG', 'PNG', 'WEBP'}:
        return False

    if image.width <= max_size[0] and image.height <= max_size[1] and orientation not in range(2, 9):
        return False

    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    save_options = {}
    if icc_profile:
        save_options['icc_profile'] = icc_profile
    if image_format == 'JPEG':
        if image.mode not in {'RGB', 'L', 'CMYK'}:
            image = image.convert('RGB')
        save_options.update(quality=92, optimize=True, progressive=True)
    elif image_format == 'WEBP':
        save_options.update(quality=92, method=6)
    else:
        save_options.update(optimize=True)
    image.save(image_path, format=image_format, **save_options)
    return True


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Course(TimeStampedModel):
    """Course model repurposed for property listings"""
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    featured_image = models.ImageField(upload_to='courses/', null=True, blank=True)
    # Fields for property listings
    location = models.CharField(max_length=300, blank=True, help_text='Location or nearest town')
    plot_size = models.CharField(max_length=50, default='50 x 100')
    extra_details = models.TextField(blank=True, help_text='Additional listing details (e.g., landmarks, access roads)')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'featured_image')
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        _optimize_image(self.featured_image, previous_image, (2400, 1800))


class CourseImage(TimeStampedModel):
    """Additional photos for a land listing with captions."""
    course = models.ForeignKey(Course, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='courses/gallery/', null=True, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Course Image'
        verbose_name_plural = 'Course Images'

    def __str__(self):
        return self.caption or f"{self.course.title} image {self.id}"

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'image')
        super().save(*args, **kwargs)
        _optimize_image(self.image, previous_image, (2400, 1800))


class BlogPost(TimeStampedModel):
    """Blog/News posts model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    featured_image = models.ImageField(upload_to='blog/')
    content = models.TextField()
    excerpt = models.CharField(max_length=500)
    author = models.CharField(max_length=100, default='Admin')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    views = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    published_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'featured_image')
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        _optimize_image(self.featured_image, previous_image, (2000, 1500))


class Testimonial(TimeStampedModel):
    """Student/Alumni testimonials model"""
    name = models.CharField(max_length=150)
    course = models.CharField(max_length=200)
    message = models.TextField()
    photo = models.ImageField(upload_to='testimonials/')
    rating = models.PositiveIntegerField(default=5, choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)])
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.name} - {self.course}"

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'photo')
        super().save(*args, **kwargs)
        _optimize_image(self.photo, previous_image, (800, 800))


class GalleryImage(TimeStampedModel):
    """Gallery images model"""
    CATEGORY_CHOICES = [
        ('main-view', 'Main View'),
        ('frontage', 'Frontage'),
        ('road-access', 'Road Access'),
        ('plot-layout', 'Plot Layout'),
        ('surroundings', 'Surroundings'),
        ('title-documents', 'Title Documents'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'order']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'image')
        super().save(*args, **kwargs)
        _optimize_image(self.image, previous_image, (2400, 1600))


class Video(TimeStampedModel):
    """YouTube video links for embedding on the site."""
    title = models.CharField(max_length=250)
    youtube_url = models.URLField(help_text='Full YouTube URL (https://www.youtube.com/watch?v=...)')
    description = models.TextField(blank=True)
    thumbnail = models.URLField(blank=True, help_text='Optional thumbnail URL (auto-extracted if left blank)')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return self.title

    def youtube_id(self):
        """Extract the video id from a YouTube URL."""
        import re
        m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{6,})', self.youtube_url or '')
        return m.group(1) if m else None

    def embed_url(self):
        vid = self.youtube_id()
        return f'https://www.youtube.com/embed/{vid}' if vid else ''

    def save(self, *args, **kwargs):
        # Auto-populate thumbnail if missing (YouTube default thumbnail)
        if not self.thumbnail:
            vid = self.youtube_id()
            if vid:
                self.thumbnail = f'https://img.youtube.com/vi/{vid}/hqdefault.jpg'
        super().save(*args, **kwargs)

    @staticmethod
    def optimize_image(image_path, size=(800, 600)):
        if os.path.exists(image_path):
            img = Image.open(image_path)
            if img.height > 600 or img.width > 800:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(image_path, quality=85, optimize=True)


class Application(TimeStampedModel):
    """Student application model"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f"{self.full_name} - {self.course.title}"


class AboutPage(models.Model):
    """About page content model"""
    title = models.CharField(max_length=300, default="About Nakuru College of Health Sciences and Management")
    history = models.TextField()
    mission = models.TextField()
    vision = models.TextField()
    values = models.TextField()
    principal_message = models.TextField(blank=True)
    principal_name = models.CharField(max_length=150, blank=True)
    principal_image = models.ImageField(upload_to='about/', null=True, blank=True)
    history_image = models.ImageField(upload_to='about/', null=True, blank=True)
    campus_description = models.TextField()
    campus_image = models.ImageField(upload_to='about/', null=True, blank=True)
    location = models.CharField(max_length=300)
    established_year = models.IntegerField(default=2024)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About Page'
        verbose_name_plural = 'About Page'

    def __str__(self):
        return "About Page"

    def save(self, *args, **kwargs):
        image_fields = ('principal_image', 'history_image', 'campus_image')
        previous_images = {
            field_name: _stored_image_name(self, field_name)
            for field_name in image_fields
        }
        super().save(*args, **kwargs)
        for field_name in image_fields:
            _optimize_image(getattr(self, field_name), previous_images[field_name], (2400, 1800))


class AboutImage(models.Model):
    """Additional images for the About page"""
    about = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='about/images/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-uploaded_at']
        verbose_name = 'About Image'
        verbose_name_plural = 'About Images'

    def __str__(self):
        return f"AboutImage {self.pk} ({self.about})"

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'image')
        super().save(*args, **kwargs)
        _optimize_image(self.image, previous_image, (2400, 1800))

    def delete(self, *args, **kwargs):
        # remove file from storage
        try:
            if self.image and default_storage.exists(self.image.name):
                default_storage.delete(self.image.name)
        except Exception:
            pass
        super().delete(*args, **kwargs)


class AboutVideo(models.Model):
    """Video files for the About page"""
    about = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='videos')
    file = models.FileField(upload_to='about/videos/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-uploaded_at']
        verbose_name = 'About Video'
        verbose_name_plural = 'About Videos'

    def __str__(self):
        return f"AboutVideo {self.pk} ({self.about})"

    def delete(self, *args, **kwargs):
        try:
            if self.file and default_storage.exists(self.file.name):
                default_storage.delete(self.file.name)
        except Exception:
            pass
        super().delete(*args, **kwargs)


# Signals to cleanup files when instances are deleted or replaced
@receiver(post_delete, sender=AboutImage)
def delete_aboutimage_file(sender, instance, **kwargs):
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception:
            pass


@receiver(post_delete, sender=AboutVideo)
def delete_aboutvideo_file(sender, instance, **kwargs):
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception:
            pass


@receiver(pre_save, sender=AboutImage)
def auto_delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = AboutImage.objects.get(pk=instance.pk)
    except AboutImage.DoesNotExist:
        return
    if old.image and old.image.name != instance.image.name:
        try:
            old.image.delete(save=False)
        except Exception:
            pass


@receiver(pre_save, sender=AboutVideo)
def auto_delete_old_video_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = AboutVideo.objects.get(pk=instance.pk)
    except AboutVideo.DoesNotExist:
        return
    if old.file and old.file.name != instance.file.name:
        try:
            old.file.delete(save=False)
        except Exception:
            pass


class ContactInfo(models.Model):
    """Contact information model"""
    phone_primary = models.CharField(max_length=20)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    email_alternative = models.EmailField(blank=True)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Kenya')
    
    # Social media links
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    
    # Google Maps
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Operating hours
    opening_hours = models.CharField(max_length=100, default="Monday - Friday: 8:00 AM - 5:00 PM")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Info'
        verbose_name_plural = 'Contact Info'

    def __str__(self):
        return "Contact Information"


class AdminProfile(models.Model):
    """Custom admin profile model"""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='admin_profile')
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='admin/', null=True, blank=True)
    bio = models.TextField(blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin Profile - {self.user.username}"

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'avatar')
        super().save(*args, **kwargs)
        _optimize_image(self.avatar, previous_image, (800, 800))


class SiteSettings(models.Model):
    """Singleton model to store site-wide settings like logo."""
    site_name = models.CharField(max_length=255, default='NCHSM', blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name or 'Site Settings'

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'logo')
        super().save(*args, **kwargs)
        _optimize_image(self.logo, previous_image, (1200, 1200))

    def logo_url(self):
        if self.logo:
            return self.logo.url
        return ''

class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team_photos/', blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Team member'
        verbose_name_plural = 'Team members'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        previous_image = _stored_image_name(self, 'photo')
        super().save(*args, **kwargs)
        _optimize_image(self.photo, previous_image, (1000, 1000))

class ContactMessage(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contact message'
        verbose_name_plural = 'Contact messages'

    def __str__(self):
        return f"{self.subject or 'Message'} from {self.email or 'anonymous'}"


class Conversation(TimeStampedModel):
    """A conversation record for admin review and follow-up."""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    listing = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f"Conversation {self.pk} - {self.subject or 'No subject'}"


class ConversationMessage(TimeStampedModel):
    """Individual messages in a conversation."""
    SENDER_CHOICES = [
        ('visitor', 'Visitor'),
        ('agent', 'Agent'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES, default='visitor')
    text = models.TextField()

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Conversation Message'
        verbose_name_plural = 'Conversation Messages'

    def __str__(self):
        return f"{self.get_sender_display()} @ {self.created_at}: {self.text[:50]}"
