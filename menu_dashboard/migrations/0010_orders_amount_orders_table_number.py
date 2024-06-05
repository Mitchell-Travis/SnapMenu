# Generated by Django 5.0.6 on 2024-06-01 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_dashboard', '0009_remove_orders_table_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='table_number',
            field=models.IntegerField(null=True),
        ),
    ]