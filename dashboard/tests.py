from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import ContactMessage


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
