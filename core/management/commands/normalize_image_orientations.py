from django.core.management.base import BaseCommand

from core.models import (
    AboutImage,
    AboutPage,
    AdminProfile,
    BlogPost,
    Course,
    CourseImage,
    GalleryImage,
    SiteSettings,
    TeamMember,
    Testimonial,
    _normalize_image_file,
)


IMAGE_FIELDS = (
    (Course, 'featured_image', (2400, 1800)),
    (CourseImage, 'image', (2400, 1800)),
    (BlogPost, 'featured_image', (2000, 1500)),
    (Testimonial, 'photo', (800, 800)),
    (GalleryImage, 'image', (2400, 1600)),
    (AboutPage, 'principal_image', (2400, 1800)),
    (AboutPage, 'history_image', (2400, 1800)),
    (AboutPage, 'campus_image', (2400, 1800)),
    (AboutImage, 'image', (2400, 1800)),
    (AdminProfile, 'avatar', (800, 800)),
    (SiteSettings, 'logo', (1200, 1200)),
    (TeamMember, 'photo', (1000, 1000)),
)


class Command(BaseCommand):
    help = 'Correct EXIF-rotated images already stored by the site.'

    def handle(self, *args, **options):
        normalized = 0
        seen_files = set()

        for model, field_name, max_size in IMAGE_FIELDS:
            for instance in model.objects.exclude(**{f'{field_name}': ''}).iterator():
                image_field = getattr(instance, field_name)
                if not image_field or image_field.name in seen_files:
                    continue
                seen_files.add(image_field.name)
                if _normalize_image_file(image_field, max_size):
                    normalized += 1
                    self.stdout.write(f'Corrected {model.__name__} {instance.pk}: {image_field.name}')

        self.stdout.write(self.style.SUCCESS(f'Finished. Corrected {normalized} image(s).'))
