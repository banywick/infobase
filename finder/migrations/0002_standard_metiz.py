# Generated by Django 5.1.5 on 2025-01-21 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Standard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=100)),
                ('type_standarts', models.CharField(choices=[('GOST', 'ГОСТ'), ('DIN', 'DIN'), ('ISO', 'ISO')], max_length=4, verbose_name='Стандарт')),
            ],
        ),
        migrations.CreateModel(
            name='Metiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('standards', models.ManyToManyField(related_name='metizes', to='finder.standard')),
            ],
        ),
    ]
