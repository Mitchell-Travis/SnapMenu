# Generated by Django 5.0.6 on 2024-06-04 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_dashboard', '0010_orders_amount_orders_table_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orders',
            old_name='amount',
            new_name='total_amount',
        ),
        migrations.RemoveField(
            model_name='orders',
            name='product',
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu_dashboard.orders')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu_dashboard.product')),
            ],
        ),
    ]