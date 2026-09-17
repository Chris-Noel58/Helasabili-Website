"""
Initial data loader for NCHSM Kikuyu Campus
This script populates the database with sample data for demonstration
Run with: python manage.py shell < load_demo_data.py
"""

from django.core.files.base import ContentFile
from core.models import (
    Course, BlogPost, Testimonial, GalleryImage,
    AboutPage, ContactInfo
)
from django.utils import timezone
from datetime import timedelta

print("Loading demo data...")

# 1. Create Contact Information
contact, created = ContactInfo.objects.get_or_create(
    defaults={
        'phone_primary': '+254 (0) 710 123 456',
        'phone_secondary': '+254 (0) 731 654 321',
        'email': 'info@nchskikuyu.ac.ke',
        'email_alternative': 'admissions@nchskikuyu.ac.ke',
        'address': 'Kikuyu Campus, Nakuru County',
        'postal_code': '20100',
        'city': 'Nakuru',
        'country': 'Kenya',
        'facebook': 'https://facebook.com/nchskikuyu',
        'twitter': 'https://twitter.com/nchskikuyu',
        'instagram': 'https://instagram.com/nchskikuyu',
        'youtube': 'https://youtube.com/nchskikuyu',
        'latitude': -0.3031,
        'longitude': 35.9102,
        'opening_hours': 'Monday - Friday: 8:00 AM - 5:00 PM, Saturday: 9:00 AM - 1:00 PM'
    }
)
if created:
    print("✓ Contact information created")
else:
    print("✓ Contact information already exists")

# 2. Create About Page
about, created = AboutPage.objects.get_or_create(
    defaults={
        'title': 'About Nakuru College of Health Sciences and Management',
        'history': 'Founded in 2015, NCHSM has been at the forefront of health sciences education in Kenya. Our Kikuyu campus was established to extend quality education closer to our students, providing a conducive learning environment with state-of-the-art facilities.',
        'mission': 'To provide quality, relevant, and accessible health sciences and management education that develops competent, ethical, and innovative professionals who contribute to societal development.',
        'vision': 'To be a leading institution of excellence in health sciences and management education, recognized locally and internationally for quality and innovation.',
        'values': 'Excellence, Integrity, Innovation, Student-centeredness, Inclusivity, Accountability, and Sustainability.',
        'principal_message': 'Welcome to NCHSM Kikuyu Campus. We are committed to providing the best learning experience and preparing our students for successful careers in health sciences and management. Our dedicated faculty, modern facilities, and supportive community create an ideal environment for learning and personal growth.',
        'principal_name': 'Dr. Sarah Kipchoge',
        'campus_description': 'The Kikuyu campus features modern classrooms, well-equipped laboratories, a comprehensive library, student residences, and recreational facilities. Our campus is designed to foster both academic excellence and personal development.',
        'location': 'Kikuyu, Nakuru County, Kenya',
        'established_year': 2015
    }
)
if created:
    print("✓ About page created")
else:
    print("✓ About page already exists")

# 3. Create Courses
courses_data = [
    {
        'title': 'Diploma in Nursing',
        'description': 'A comprehensive two-year program preparing students for nursing practice. Covers anatomy, physiology, pharmacology, and clinical nursing skills.',
        'duration': '2 Years',
        'intake_period': 'january',
        'fees': 150000,
        'is_active': True,
        'order': 1
    },
    {
        'title': 'Diploma in Clinical Medicine',
        'description': 'Three-year program focusing on clinical diagnosis and patient management. Includes extensive practical training in hospitals.',
        'duration': '3 Years',
        'intake_period': 'april',
        'fees': 180000,
        'is_active': True,
        'order': 2
    },
    {
        'title': 'Certificate in Health Information Management',
        'description': 'One-year intensive program on health data management, medical records, and healthcare information systems.',
        'duration': '1 Year',
        'intake_period': 'july',
        'fees': 85000,
        'is_active': True,
        'order': 3
    },
    {
        'title': 'Diploma in Business Management',
        'description': 'Two-year program covering business administration, finance, human resources, and organizational management.',
        'duration': '2 Years',
        'intake_period': 'september',
        'fees': 120000,
        'is_active': True,
        'order': 4
    },
]

for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        title=course_data['title'],
        defaults=course_data
    )
    if created:
        print(f"✓ Course created: {course.title}")

# 4. Create Blog Posts
blog_data = [
    {
        'title': 'Welcome to NCHSM Kikuyu Campus',
        'slug': 'welcome-to-nchsm-kikuyu-campus',
        'content': 'We are excited to announce the opening of our new Kikuyu campus. This facility brings quality health sciences and management education closer to our students. The campus features modern teaching facilities, well-equipped laboratories, and a supportive learning environment.',
        'excerpt': 'NCHSM opens new Kikuyu campus with modern facilities',
        'author': 'Administration',
        'status': 'published',
        'is_featured': True,
    },
    {
        'title': 'New Intakes for 2024',
        'slug': 'new-intakes-2024',
        'content': 'NCHSM is now accepting applications for our 2024 intakes. We are recruiting qualified candidates for all our programs. Applications are open in January, April, July, and September. Visit our apply page to submit your application.',
        'excerpt': 'New student intakes are now open for all programs',
        'author': 'Admissions Office',
        'status': 'published',
        'is_featured': True,
    },
    {
        'title': 'Our Commitment to Quality Education',
        'slug': 'commitment-to-quality',
        'content': 'At NCHSM, we are dedicated to providing quality education that meets international standards. Our curriculum is regularly updated to reflect current industry practices and trends. Our faculty comprises experienced professionals committed to student success.',
        'excerpt': 'Discover our commitment to academic excellence',
        'author': 'Academic Office',
        'status': 'published',
        'is_featured': False,
    },
]

for blog_data_item in blog_data:
    blog, created = BlogPost.objects.get_or_create(
        title=blog_data_item['title'],
        defaults={
            **blog_data_item,
            'published_date': timezone.now() - timedelta(days=days_offset)
        }
    )
    if created:
        print(f"✓ Blog post created: {blog.title}")

# 5. Create Testimonials
testimonials_data = [
    {
        'name': 'Grace Kipchoge',
        'course': 'Diploma in Nursing',
        'message': 'NCHSM provided me with excellent clinical training and support. The faculty is knowledgeable and dedicated to student success. I landed a job immediately after graduation.',
        'rating': 5,
        'is_active': True,
        'order': 1
    },
    {
        'name': 'Peter Karanja',
        'course': 'Diploma in Clinical Medicine',
        'message': 'The practical experience I gained here was invaluable. Modern labs and experienced instructors made my learning journey memorable. Highly recommended!',
        'rating': 5,
        'is_active': True,
        'order': 2
    },
    {
        'name': 'Elizabeth Muriuki',
        'course': 'Diploma in Business Management',
        'message': 'Great institution with supportive staff and excellent curriculum. I now manage a small business successfully thanks to the skills I acquired here.',
        'rating': 4,
        'is_active': True,
        'order': 3
    },
]

for testimonial_data in testimonials_data:
    testimonial, created = Testimonial.objects.get_or_create(
        name=testimonial_data['name'],
        defaults=testimonial_data
    )
    if created:
        print(f"✓ Testimonial created: {testimonial.name}")

# 6. Create Gallery Images
gallery_data = [
    {
        'title': 'Main Classroom Block',
        'category': 'classroom',
        'description': 'Modern classroom facilities with multimedia equipment',
        'is_active': True,
        'order': 1
    },
    {
        'title': 'Clinical Laboratory',
        'category': 'lab',
        'description': 'Well-equipped laboratory for practical training',
        'is_active': True,
        'order': 2
    },
    {
        'title': 'Campus View',
        'category': 'campus',
        'description': 'Beautiful view of the Kikuyu campus',
        'is_active': True,
        'order': 3
    },
    {
        'title': 'Graduation Ceremony',
        'category': 'graduation',
        'description': 'NCHSM Graduation Ceremony 2023',
        'is_active': True,
        'order': 4
    },
]

for gallery_data_item in gallery_data:
    gallery, created = GalleryImage.objects.get_or_create(
        title=gallery_data_item['title'],
        defaults=gallery_data_item
    )
    if created:
        print(f"✓ Gallery image created: {gallery.title}")

print("\n✓ Demo data loading completed successfully!")
print("\nYou can now log in to the dashboard and see the sample data.")
print("Dashboard URL: http://localhost:8000/dashboard/login/")
