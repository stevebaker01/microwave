# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-16 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_playlist_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='version',
            field=models.TextField(blank=True, max_length=50),
        ),
    ]
