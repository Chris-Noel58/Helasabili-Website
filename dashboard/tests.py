from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from core.models import AboutPage, ContactMessage, TeamMember


class DashboardEnquiriesViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='StrongPass123',
            is_staff=True,
            is_superuser=True,
        )
        ContactMessage.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            subject='Test enquiry',
            message='I would like more information about the property.',
        )

    def test_enquiries_page_loads_for_admin(self):
        self.client.login(username='adminuser', password='StrongPass123')
        response = self.client.get('/dashboard/enquiries/', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enquiries')
        self.assertContains(response, 'Jane Doe')

    def test_team_member_can_be_added_with_clear_photo_then_edited(self):
        self.client.login(username='adminuser', password='StrongPass123')
        image_buffer = BytesIO()
        Image.new('RGB', (1200, 900), color='navy').save(image_buffer, format='PNG')
        image_buffer.seek(0)

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post('/dashboard/team/add/', {
                'name': 'Jane Doe',
                'title': 'Director',
                'bio': 'Leads the team.',
                'order': 1,
                'is_active': 'on',
                'photo': SimpleUploadedFile('jane.png', image_buffer.read(), content_type='image/png'),
            })

            self.assertRedirects(response, '/dashboard/team/')
            member = TeamMember.objects.get(name='Jane Doe')
            self.assertTrue(Path(member.photo.path).is_file())
            with Image.open(member.photo.path) as optimized_photo:
                self.assertEqual(optimized_photo.size, (1000, 750))

            list_response = self.client.get('/dashboard/team/')
            self.assertContains(list_response, 'Jane Doe')
            self.assertContains(list_response, member.photo.url)

            AboutPage.objects.create(
                history='Our story.',
                mission='Our mission.',
                vision='Our vision.',
                values='Our values.',
                campus_description='About us.',
                location='Nairobi',
            )
            public_response = self.client.get('/about/')
            self.assertContains(public_response, 'Company Details')
            self.assertContains(public_response, 'Our services:')
            self.assertContains(public_response, 'about-cta')
            self.assertNotContains(public_response, 'Campus Details')
            self.assertNotContains(public_response, 'Modern classrooms')
            self.assertContains(public_response, 'team-member-photo')
            self.assertContains(public_response, member.photo.url)

            edit_response = self.client.post(f'/dashboard/team/{member.pk}/edit/', {
                'name': 'Jane Smith',
                'title': 'Executive Director',
                'bio': 'Updated bio.',
                'order': 2,
                'is_active': 'on',
            })
            self.assertRedirects(edit_response, '/dashboard/team/')
            member.refresh_from_db()
            self.assertEqual(member.name, 'Jane Smith')
            self.assertEqual(member.title, 'Executive Director')
            self.assertTrue(member.is_active)
            self.assertTrue(Path(member.photo.path).is_file())

            self.assertEqual(
                self.client.get(f'/dashboard/team/{member.pk}/delete/').status_code,
                405,
            )
            delete_response = self.client.post(f'/dashboard/team/{member.pk}/delete/')
            self.assertRedirects(delete_response, '/dashboard/team/')
            self.assertFalse(TeamMember.objects.filter(pk=member.pk).exists())
