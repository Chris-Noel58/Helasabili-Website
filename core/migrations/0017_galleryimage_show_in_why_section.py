from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_galleryimage_show_in_home_hero'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryimage',
            name='show_in_why_section',
            field=models.BooleanField(
                default=False,
                verbose_name='Use as Why Choose background',
            ),
        ),
    ]
