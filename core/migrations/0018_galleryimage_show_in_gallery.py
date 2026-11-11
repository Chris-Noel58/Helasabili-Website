from django.db import migrations, models


def select_active_gallery_images(apps, schema_editor):
    GalleryImage = apps.get_model('core', 'GalleryImage')
    GalleryImage.objects.using(schema_editor.connection.alias).filter(
        is_active=True,
    ).update(show_in_gallery=True)


def clear_gallery_image_selection(apps, schema_editor):
    GalleryImage = apps.get_model('core', 'GalleryImage')
    GalleryImage.objects.using(schema_editor.connection.alias).update(show_in_gallery=False)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_galleryimage_show_in_why_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryimage',
            name='show_in_gallery',
            field=models.BooleanField(
                default=False,
                verbose_name='Show in Gallery & Home',
            ),
        ),
        migrations.RunPython(
            select_active_gallery_images,
            clear_gallery_image_selection,
        ),
    ]
