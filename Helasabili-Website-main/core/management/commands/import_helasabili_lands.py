"""
Management command to import lands from the Helasabili database
and create/update Course records for display on the website.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connections
from core.models import Course
from decimal import Decimal


class Command(BaseCommand):
    help = 'Import product names from the Helasabili database Inventories table and create Course records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Create demo listings if database connection fails',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.WARNING('Fetching lands from Helasabili database...'))
            
            try:
                # Use raw database connection to query Helasabili
                conn = connections['helasabili']
                with conn.cursor() as cursor:
                    cursor.execute('SELECT id, "ProductName" FROM "Inventories" ORDER BY id')
                    inventories = cursor.fetchall()
                
                count = len(inventories)
                self.stdout.write(f'Found {count} land listings')
                
                if count == 0:
                    self.stdout.write(self.style.WARNING('No inventories found'))
                    if options['demo']:
                        self.create_demo_listings()
                    return
                
                created_count = 0
                updated_count = 0
                error_count = 0
                
                with transaction.atomic():
                    for inv_id, product_name in inventories:
                        try:
                            if not product_name:
                                continue
                                
                            slug = f"helasabili-{inv_id}-{product_name.lower()[:50].replace(' ', '-').replace('/', '-')}"[:100]
                            
                            course, created = Course.objects.get_or_create(
                                slug=slug,
                                defaults={
                                    'title': product_name[:200],
                                    'description': f"Land/Property: {product_name}",
                                    'location': 'Helasabili',
                                    'fees': Decimal('0.00'),
                                    'is_active': True,
                                }
                            )
                            
                            if created:
                                created_count += 1
                                self.stdout.write(self.style.SUCCESS(f'✓ Created: {product_name}'))
                            else:
                                course.title = product_name[:200]
                                course.description = f"Land/Property: {product_name}"
                                course.save()
                                updated_count += 1
                        
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
                
                self.stdout.write(self.style.SUCCESS(f'\n✓ Created: {created_count}'))
                self.stdout.write(self.style.SUCCESS(f'✓ Updated: {updated_count}'))
                if error_count > 0:
                    self.stdout.write(self.style.ERROR(f'✗ Errors: {error_count}'))
                self.stdout.write(self.style.SUCCESS(f'✓ Total: {created_count + updated_count + error_count} processed'))
            
            except Exception as db_error:
                self.stdout.write(self.style.ERROR(f'Database connection error: {str(db_error)}'))
                if options['demo']:
                    self.stdout.write(self.style.WARNING('Creating demo listings instead...'))
                    self.create_demo_listings()
                else:
                    self.stdout.write(self.style.WARNING('Use --demo flag to create demo listings'))
        
        except Exception as e:
            raise CommandError(f'Error: {str(e)}')
    
    def create_demo_listings(self):
        """Create demo listings for testing"""
        demo_lands = [
            'Kahawa west',
            'Kikuyu Estate',
            'Limuru Gardens',
            'Gitaru Plot',
            'Muhoho Valley',
            'Kiambu Heights',
        ]
        
        created_count = 0
        for land_name in demo_lands:
            slug = f"demo-{land_name.lower().replace(' ', '-')}"
            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': land_name,
                    'description': f"Land/Property: {land_name}",
                    'location': 'Helasabili',
                    'fees': Decimal('100000.00'),
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Demo Created: {land_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nDemo listings created: {created_count}'))
