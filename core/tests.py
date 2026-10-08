from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from PIL import Image

from core.models import Course, CourseImage, GalleryImage


class CourseImageGalleryTests(TestCase):
    def test_course_can_have_multiple_images_with_captions(self):
        course = Course.objects.create(
            title='Test Land',
            description='Description',
            location='Nakuru',
            plot_size='50 x 100',
            fees='150000.00',
            is_active=True,
        )

        image1 = CourseImage.objects.create(
            course=course,
            caption='Front view',
            order=1,
        )
        image2 = CourseImage.objects.create(
            course=course,
            caption='Back view',
            order=2,
        )

        self.assertEqual(course.images.count(), 2)
        self.assertEqual(list(course.images.values_list('caption', flat=True)), ['Front view', 'Back view'])
        self.assertIn(image1, course.images.all())
        self.assertIn(image2, course.images.all())


class GalleryImageQualityTests(TestCase):
    def make_rotated_jpeg(self, size=(120, 60)):
        image_buffer = BytesIO()
        exif = Image.Exif()
        exif[274] = 6
        Image.new('RGB', size, color='navy').save(image_buffer, format='JPEG', exif=exif)
        image_buffer.seek(0)
        return image_buffer

    def test_uploaded_exif_rotated_photo_is_saved_upright(self):
        image_buffer = self.make_rotated_jpeg()

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            gallery_image = GalleryImage.objects.create(
                title='Rotated upload',
                category='other',
                image=SimpleUploadedFile('rotated.jpg', image_buffer.read(), content_type='image/jpeg'),
            )

            with Image.open(gallery_image.image.path) as upright_image:
                self.assertEqual(upright_image.size, (60, 120))
                self.assertEqual(upright_image.getexif().get(274), None)

    def test_command_corrects_existing_exif_rotated_photos(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            gallery_image = GalleryImage(
                title='Legacy rotated photo',
                category='other',
            )
            gallery_image.image.name = 'gallery/legacy-rotated.jpg'
            GalleryImage.objects.bulk_create([gallery_image])

            image_path = Path(media_root) / gallery_image.image.name
            image_path.parent.mkdir(parents=True)
            image_path.write_bytes(self.make_rotated_jpeg().read())

            call_command('normalize_image_orientations', verbosity=0)

            with Image.open(image_path) as upright_image:
                self.assertEqual(upright_image.size, (60, 120))
                self.assertEqual(upright_image.getexif().get(274), None)

    def test_large_upload_retains_display_resolution_and_is_not_recompressed_on_save(self):
        image_buffer = BytesIO()
        Image.new('RGB', (3000, 2000), color='navy').save(image_buffer, format='JPEG', quality=100)
        image_buffer.seek(0)

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            gallery_image = GalleryImage.objects.create(
                title='High-resolution upload',
                category='other',
                image=SimpleUploadedFile('high-resolution.jpg', image_buffer.read(), content_type='image/jpeg'),
            )
            image_path = Path(gallery_image.image.path)

            with Image.open(image_path) as optimized_image:
                self.assertEqual(optimized_image.size, (2400, 1600))
                self.assertEqual(optimized_image.format, 'JPEG')

            optimized_contents = image_path.read_bytes()
            gallery_image.description = 'Updating text should not recompress the original upload.'
            gallery_image.save()

            self.assertEqual(image_path.read_bytes(), optimized_contents)
