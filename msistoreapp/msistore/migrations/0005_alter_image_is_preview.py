# Generated by Django 4.2.7 on 2023-11-09 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msistore', '0004_rename_ispreview_image_is_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='is_Preview',
            field=models.BooleanField(),
        ),
    ]