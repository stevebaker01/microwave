# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-01 03:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20160930_2125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spotifyprofile',
            old_name='durations',
            new_name='duration',
        ),
    ]
