# Generated by Django 5.0.6 on 2024-05-28 00:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu_dashboard', '0004_remove_customer_address_remove_customer_mobile_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='address',
        ),
        migrations.RemoveField(
            model_name='orders',
            name='email',
        ),
    ]
