# Generated by Django 5.1.5 on 2025-01-15 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Remains',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=50, null=True, verbose_name='Комментарий')),
                ('code', models.CharField(max_length=50, null=True, verbose_name='Код')),
                ('article', models.TextField(null=True, verbose_name='Артикул')),
                ('party', models.CharField(max_length=9, null=True, verbose_name='Партия')),
                ('title', models.TextField(null=True, verbose_name='Наименование')),
                ('base_unit', models.CharField(max_length=10, null=True, verbose_name='Единица')),
                ('project', models.CharField(max_length=30, null=True, verbose_name='Проект')),
                ('quantity', models.FloatField(blank=True, null=True, verbose_name='Количество')),
                ('price', models.IntegerField(null=True)),
            ],
            options={
                'verbose_name': 'Остаток',
                'verbose_name_plural': 'Остатки',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(blank=True, null=True, verbose_name='Пользователь')),
                ('text', models.TextField(verbose_name='Отзыв')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
    ]
