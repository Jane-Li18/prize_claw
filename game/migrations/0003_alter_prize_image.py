# Generated by Django 5.2.1 on 2025-05-21 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_alter_prize_probability'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prize',
            name='image',
            field=models.URLField(default=1, max_length=500),
            preserve_default=False,
        ),
    ]
