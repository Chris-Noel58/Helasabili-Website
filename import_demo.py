#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nchskikuyu.settings')
django.setup()

from core.models import Course
from decimal import Decimal

# Clear existing demo courses
Course.objects.filter(slug__startswith='helasabili-').delete()

# Create 103 demo listings
products = [
    "Sample Product 9",
    "Sample Product 9 - Portion Sample Product 9-1",
    "Sample Product 9 - Portion Sample Product 9-2",
    "Sample Product 9 - Portion Sample Product 9-3",
    "Sample Product 9 - Portion Sample Product 9-4",
    "Sample Product 9 - Portion Sample Product 9-5",
    "Sample Product 9 - Portion Sample Product 9-6",
    "NAIVASHA/OLJORAI PHASE 11/1558",
    "NAIVASHA/OLJORAI PHASE 11/1558 - Portion NAIVASHA/OLJORAI PHASE 11/1558",
    "NAIVASHA/OLJORAI PHASE 11/1558 - Portion NAIVASHA/OLJORAI PHASE 11/1558-2",
]

created_count = 0
for i in range(1, 104):
    if i <= len(products):
        title = products[i-1]
    else:
        title = f"Land Plot {i}"
    
    slug = f"helasabili-{i}-{title.lower()[:50].replace(' ', '-').replace('/', '-')}"[:100]
    
    course, created = Course.objects.get_or_create(
        slug=slug,
        defaults={
            'title': title[:200],
            'description': f"Land/Property: {title}",
            'location': 'Helasabili',
            'fees': Decimal('0.00'),
            'is_active': True,
        }
    )
    if created:
        created_count += 1
        print(f"✓ Created: {title}")

total = Course.objects.count()
print(f"\n{'='*50}")
print(f"✓ Successfully created: {created_count}")
print(f"✓ Total courses in database: {total}")
print(f"{'='*50}")
