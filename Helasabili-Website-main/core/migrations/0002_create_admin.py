from django.db import migrations


def create_admin(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = 'admin'
    email = 'admin@localhost'
    password = 'Admin@123'

    user, created = User.objects.update_or_create(
        username=username,
        defaults={'email': email, 'is_staff': True, 'is_superuser': True},
    )
    user.set_password(password)
    user.save()


def remove_admin(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        u = User.objects.get(username='admin')
        u.delete()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin, reverse_code=remove_admin),
    ]
