# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-21 22:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_remove_track_genres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='spotify_id',
            field=models.CharField(blank=True, db_index=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='composer',
            name='spotify_id',
            field=models.CharField(blank=True, db_index=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='genre',
            name='domain',
            field=models.CharField(choices=[('spotify', 'spotify')], max_length=100),
        ),
        migrations.AlterField(
            model_name='spotifyprofile',
            name='id',
            field=models.CharField(db_index=True, max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='track',
            name='spotify_id',
            field=models.CharField(blank=True, db_index=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='spotify_id',
            field=models.CharField(blank=True, db_index=True, max_length=100, unique=True),
        ),
    ]