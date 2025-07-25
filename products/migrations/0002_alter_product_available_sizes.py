# Generated by Django 5.1.5 on 2025-07-20 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='available_sizes',
            field=models.CharField(help_text='Enter sizes separated by commas. For hair care: S,M,L. For shoes: 389,40. For perfumes: 50ml,100ml', max_length=200),
        ),
    ]
