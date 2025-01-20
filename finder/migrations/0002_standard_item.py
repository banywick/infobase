# Generated by Django 5.1.5 on 2025-01-20 19:50

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
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('bolt', 'Болт'), ('nut', 'Гайка'), ('washer', 'Шайба'), ('ring', 'Кольцо'), ('screw', 'Винт'), ('pin', 'Шпилька'), ('split_pin', 'Шплинт'), ('dowel', 'Штифт'), ('key', 'Шпонка'), ('rivet', 'Заклепка'), ('threaded_insert', 'Вставка (втулка) резьбовая (сменная)'), ('clamp', 'Хомут'), ('half_ring', 'Полукольцо')], max_length=50)),
                ('standards', models.ManyToManyField(related_name='items', to='finder.standard')),
            ],
        ),
    ]