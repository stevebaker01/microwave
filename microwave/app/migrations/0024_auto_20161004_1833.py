# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-04 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_auto_20161004_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='isrc',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
