from django.core.management.base import BaseCommand

from core.models import AboutImage, AboutPage, BlogPost, Course, CourseImage, GalleryImage
from core.templatetags.ui import _thumbs_for


class Command(BaseCommand):
    help = 'Pre-generate WebP thumbnails used by the public site so first page views stay fast.'

    def handle(self, *args, **options):
        sources = [
            (Course, ['featured_image']),
            (CourseImage, ['image']),
            (GalleryImage, ['image']),
            (BlogPost, ['featured_image']),
            (AboutImage, ['image']),
            (AboutPage, ['history_image', 'campus_image', 'principal_image']),
        ]
        done = failed = 0
        for model, fields in sources:
            for obj in model.objects.all().iterator():
                for field in fields:
                    file = getattr(obj, field, None)
                    if not file:
                        continue
                    if _thumbs_for(file):
                        done += 1
                    else:
                        failed += 1
                        self.stderr.write(f'Skipped {model.__name__} {obj.pk}: {file.name}')
        self.stdout.write(self.style.SUCCESS(f'Thumbnails ready for {done} image(s); {failed} skipped.'))
