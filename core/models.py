from django.db import models
from django.core.validators import URLValidator, EmailValidator
from django.utils.text import slugify
from PIL import Image
import os
from django.utils import timezone
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Course(TimeStampedModel):
    """Course model for various programs offered"""
    INTAKE_CHOICES = [
        ('january', 'January'),
        ('april', 'April'),
        ('july', 'July'),
        ('september', 'September'),
    ]
    
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    duration = models.CharField(max_length=50, help_text="e.g., 2 Years, 3 Months")
    intake_period = models.CharField(max_length=20, choices=INTAKE_CHOICES)
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    featured_image = models.ImageField(upload_to='courses/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Optimize image on save
        if self.featured_image:
            self.optimize_image(self.featured_image.path)

    @staticmethod
    def optimize_image(image_path, size=(400, 300)):
        """Optimize image size"""
        if os.path.exists(image_path):
            img = Image.open(image_path)
            if img.height > 300 or img.width > 400:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(image_path, quality=85, optimize=True)


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
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        if self.featured_image:
            self.optimize_image(self.featured_image.path)

    @staticmethod
    def optimize_image(image_path, size=(600, 400)):
        if os.path.exists(image_path):
            img = Image.open(image_path)
            if img.height > 400 or img.width > 600:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(image_path, quality=85, optimize=True)


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
        super().save(*args, **kwargs)
        if self.photo:
            self.optimize_image(self.photo.path)

    @staticmethod
    def optimize_image(image_path, size=(150, 150)):
        if os.path.exists(image_path):
            img = Image.open(image_path)
            if img.height > 150 or img.width > 150:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(image_path, quality=85, optimize=True)


class GalleryImage(TimeStampedModel):
    """Gallery images model"""
    CATEGORY_CHOICES = [
        ('classroom', 'Classroom'),
        ('event', 'Event'),
        ('graduation', 'Graduation'),
        ('lab', 'Lab'),
        ('campus', 'Campus Life'),
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
        super().save(*args, **kwargs)
        if self.image:
            self.optimize_image(self.image.path)

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
        super().save(*args, **kwargs)
        # Optimize saved image
        if self.image and default_storage.exists(self.image.name):
            try:
                img = Image.open(self.image.path)
                max_size = (1200, 900)
                if img.height > max_size[1] or img.width > max_size[0]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(self.image.path, quality=85, optimize=True)
            except Exception:
                pass

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
