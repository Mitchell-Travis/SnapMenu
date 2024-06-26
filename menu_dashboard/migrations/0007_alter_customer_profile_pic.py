# Generated by Django 5.0.6 on 2024-05-28 00:58

import menu_dashboard.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_dashboard', '0006_remove_orders_mobile_customer_mobile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='profile_pic',
            field=models.ImageField(blank=True, default=menu_dashboard.models.default_profile_pic, null=True, upload_to='profile_pic/CustomerProfilePic/'),
        ),
    ]
