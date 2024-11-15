# Generated by Django 5.0.6 on 2024-07-30 19:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_dashboard', '0008_alter_orders_order_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='delivered',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='delivery_time',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='deliveryrequest',
            name='request_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='deliveryrequest',
            name='status',
            field=models.CharField(db_index=True, default='Pending', max_length=50),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateField(auto_now_add=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='name',
            field=models.CharField(db_index=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Order Confirmed', 'Order Confirmed'), ('Cooking', 'Cooking'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered')], db_index=True, default='Pending', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('Available', 'Available'), ('Unavailable', 'Unavailable')], db_index=True, default='Available', max_length=20),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='restaurant_name',
            field=models.CharField(blank=True, db_index=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='rider',
            name='is_available',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='table',
            name='table_number',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='topuprequest',
            name='processed',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='topuprequest',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='usercode',
            name='code',
            field=models.CharField(db_index=True, max_length=6, unique=True),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['user'], name='menu_dashbo_user_id_5770b8_idx'),
        ),
        migrations.AddIndex(
            model_name='delivery',
            index=models.Index(fields=['delivery_request', 'delivered'], name='menu_dashbo_deliver_8cc99d_idx'),
        ),
        migrations.AddIndex(
            model_name='deliveryrequest',
            index=models.Index(fields=['order', 'rider', 'status'], name='menu_dashbo_order_i_13045f_idx'),
        ),
        migrations.AddIndex(
            model_name='earnings',
            index=models.Index(fields=['order'], name='menu_dashbo_order_i_1dae21_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['name', 'date'], name='menu_dashbo_name_307485_idx'),
        ),
        migrations.AddIndex(
            model_name='orderproduct',
            index=models.Index(fields=['order', 'product'], name='menu_dashbo_order_i_c33636_idx'),
        ),
        migrations.AddIndex(
            model_name='orders',
            index=models.Index(fields=['customer', 'restaurant', 'status', 'order_date'], name='menu_dashbo_custome_64a537_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['restaurant', 'category', 'status'], name='menu_dashbo_restaur_256584_idx'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['restaurant_name'], name='menu_dashbo_restaur_7ccfba_idx'),
        ),
        migrations.AddIndex(
            model_name='table',
            index=models.Index(fields=['restaurant', 'table_number'], name='menu_dashbo_restaur_b550b2_idx'),
        ),
        migrations.AddIndex(
            model_name='topuprequest',
            index=models.Index(fields=['user_code', 'processed', 'timestamp'], name='menu_dashbo_user_co_de3433_idx'),
        ),
        migrations.AddIndex(
            model_name='wallet',
            index=models.Index(fields=['user'], name='menu_dashbo_user_id_8a84bc_idx'),
        ),
    ]
