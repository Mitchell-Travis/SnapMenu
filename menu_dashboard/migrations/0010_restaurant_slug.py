# Generated by Django 5.0.6 on 2024-09-02 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_dashboard', '0009_alter_delivery_delivered_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='slug',
            field=models.SlugField(blank=True, max_length=40, unique=True),
        ),
    ]
