# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-14 04:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='summary',
            field=models.TextField(blank=True, max_length=2500),
        ),
        migrations.AddField(
            model_name='playlist',
            name='title',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]