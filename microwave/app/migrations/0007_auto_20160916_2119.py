# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-16 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_playlist_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='version',
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
