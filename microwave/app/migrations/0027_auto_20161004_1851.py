# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-04 18:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20161004_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='upc',
            field=models.BigIntegerField(blank=True),
        ),
    ]
