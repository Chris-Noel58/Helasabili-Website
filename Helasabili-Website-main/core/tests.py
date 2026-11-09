from django.test import TestCase

from core.models import Course, CourseImage


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
