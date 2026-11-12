from datetime import timedelta
import json
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from core.forms import AboutPageForm
from core.models import Course, CourseImage, CustomerReview, GalleryImage, SiteVisitBooking
from core.rich_text import sanitize_rich_text
from website.google_reviews import fetch_google_reviews


class RichTextSanitizerTests(SimpleTestCase):
    def test_preserves_formatting_and_multiline_plain_text(self):
        self.assertEqual(
            sanitize_rich_text('<p><strong>Company</strong></p><ol><li>Trust</li></ol>'),
            '<p><strong>Company</strong></p><ol><li>Trust</li></ol>',
        )
        self.assertEqual(
            sanitize_rich_text('<ol><li data-list="bullet">Trust</li></ol>'),
            '<ul><li>Trust</li></ul>',
        )
        self.assertEqual(
            sanitize_rich_text('First line\nSecond line'),
            'First line<br>Second line',
        )

    def test_removes_unsafe_markup_and_links(self):
        sanitized = sanitize_rich_text(
            '<p>Safe <script>alert(1)</script><a href="javascript:alert(1)">link</a></p>'
        )
        self.assertEqual(sanitized, '<p>Safe alert(1)<a>link</a></p>')

    def test_about_form_keeps_formatting_when_cleaning_content(self):
        form = AboutPageForm(data={
            'title': 'About',
            'history': '<p><strong>History</strong></p>',
            'mission': 'Mission',
            'vision': 'Vision',
            'values': '<ol><li data-list="ordered">Integrity</li></ol>',
            'principal_message': 'Welcome',
            'principal_name': '',
            'campus_description': 'Company',
            'location': 'Nakuru',
            'established_year': '2009',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['history'], '<p><strong>History</strong></p>')
        self.assertEqual(form.cleaned_data['values'], '<ol><li>Integrity</li></ol>')


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


class FeaturedProjectTests(TestCase):
    def setUp(self):
        created_at = timezone.now()
        for index in range(7):
            project = Course.objects.create(
                title=f'Project {index}',
                description=f'Description for project {index}',
                is_active=True,
            )
            Course.objects.filter(pk=project.pk).update(
                created_at=created_at + timedelta(days=index),
            )

    def test_homepage_shows_six_newest_projects_in_order(self):
        response = self.client.get('/')

        self.assertEqual(
            [project.title for project in response.context['courses']],
            [f'Project {index}' for index in range(6, 0, -1)],
        )
        self.assertContains(response, 'View Project', count=6)

    def test_listings_page_shows_all_projects_without_pagination(self):
        response = self.client.get('/listings/?page=1')

        self.assertEqual(response.context['courses'].count(), 7)
        self.assertNotContains(response, 'page-link')


class CustomerReviewTests(TestCase):
    def test_dashboard_links_to_customer_review_moderation(self):
        admin_user = get_user_model().objects.create_superuser(
            username='review-admin',
            email='review-admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin_user)

        response = self.client.get('/dashboard/testimonials/')

        self.assertContains(response, 'Review Customer Submissions')
        self.assertContains(response, reverse('admin:core_customerreview_changelist'))

    def test_submitted_review_waits_for_approval(self):
        response = self.client.post('/testimonials/', {
            'name': 'Customer One',
            'email': 'customer@example.com',
            'rating': '5',
            'message': 'A clear and helpful buying process.',
            'publication_consent': 'on',
        })

        self.assertRedirects(response, '/testimonials/')
        review = CustomerReview.objects.get(email='customer@example.com')
        self.assertEqual(review.status, CustomerReview.STATUS_PENDING)
        self.assertNotContains(self.client.get('/testimonials/'), 'A clear and helpful buying process.')

        review.status = CustomerReview.STATUS_APPROVED
        review.save()
        self.assertContains(self.client.get('/testimonials/'), 'A clear and helpful buying process.')

    def test_review_requires_publication_consent(self):
        response = self.client.post('/testimonials/', {
            'name': 'Customer One',
            'email': 'customer@example.com',
            'rating': '5',
            'message': 'Please share this review.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomerReview.objects.count(), 0)

    def test_approved_review_is_visible_on_homepage(self):
        CustomerReview.objects.create(
            name='Approved Customer',
            email='approved@example.com',
            rating=5,
            message='A great experience.',
            status=CustomerReview.STATUS_APPROVED,
        )

        self.assertContains(self.client.get('/'), 'A great experience.')

    @override_settings(GOOGLE_PLACES_API_KEY='test-key', GOOGLE_PLACE_ID='place-id')
    @patch('website.google_reviews.urlopen')
    def test_google_reviews_include_attribution(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(json.dumps({
            'reviews': [{
                'rating': 5,
                'text': {'text': 'Excellent service.'},
                'authorAttribution': {
                    'displayName': 'Google Customer',
                    'uri': 'https://www.google.com/maps/contrib/123',
                },
                'publishTime': '2026-10-01T10:00:00Z',
                'relativePublishTimeDescription': 'a month ago',
            }],
        }).encode())

        reviews = fetch_google_reviews()

        self.assertEqual(reviews[0]['name'], 'Google Customer')
        self.assertEqual(reviews[0]['author_url'], 'https://www.google.com/maps/contrib/123')


class SiteVisitBookingTests(TestCase):
    def setUp(self):
        self.project = Course.objects.create(
            title='Nakuru View',
            description='A property project in Nakuru.',
            is_active=True,
        )

    def booking_data(self, preferred_date=None):
        return {
            'customer_name': 'Alex Customer',
            'email': 'alex@example.com',
            'phone': '+254700000000',
            'property_project': str(self.project.pk),
            'preferred_date': (preferred_date or timezone.localdate() + timedelta(days=3)).isoformat(),
            'message': 'Please call before the visit.',
        }

    def test_site_visit_popup_is_available_on_the_homepage(self):
        response = self.client.get(reverse('website:home'))

        self.assertContains(response, 'Plan a site visit')
        self.assertContains(response, reverse('website:site_visit_booking'))
        self.assertContains(response, 'site_visit_popup.js')

    def test_site_visit_request_is_saved_for_dashboard_review(self):
        response = self.client.post(
            reverse('website:site_visit_booking'),
            self.booking_data(),
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(json.loads(response.content)['success'])
        booking = SiteVisitBooking.objects.get(email='alex@example.com')
        self.assertEqual(booking.status, SiteVisitBooking.STATUS_REQUESTED)
        self.assertEqual(booking.property_title, self.project.title)

        admin_user = get_user_model().objects.create_superuser(
            username='site-visit-admin',
            email='site-visit-admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin_user)
        dashboard_response = self.client.get(reverse('dashboard:site_visit_bookings_list'))
        self.assertContains(dashboard_response, 'Alex Customer')
        self.assertContains(dashboard_response, 'Nakuru View')

        update_response = self.client.post(
            reverse('dashboard:site_visit_booking_update', args=[booking.pk]),
            {'status': SiteVisitBooking.STATUS_CONFIRMED},
        )
        self.assertRedirects(update_response, reverse('dashboard:site_visit_bookings_list'))
        booking.refresh_from_db()
        self.assertEqual(booking.status, SiteVisitBooking.STATUS_CONFIRMED)

    def test_site_visit_request_rejects_a_past_date(self):
        response = self.client.post(
            reverse('website:site_visit_booking'),
            self.booking_data(timezone.localdate() - timedelta(days=1)),
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('preferred_date', json.loads(response.content)['errors'])
        self.assertEqual(SiteVisitBooking.objects.count(), 0)
