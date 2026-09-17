from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create or update a superuser with provided username, email and password.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username for the superuser')
        parser.add_argument('--email', type=str, required=True, help='Email for the superuser')
        parser.add_argument('--password', type=str, required=True, help='Password for the superuser')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']

        user, created = User.objects.update_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True},
        )
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser updated: {username}'))
