# Generated by Django 5.0.6 on 2024-07-02 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_dashboard', '0004_earnings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earnings',
            name='currency',
            field=models.CharField(default='100LRD', max_length=3),
        ),
    ]