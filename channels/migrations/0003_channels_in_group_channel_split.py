# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-12-27 16:12
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0002_auto_20171220_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='channels_in_group',
            name='channel_split',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(1), django.core.validators.MinValueValidator(0)]),
        ),
    ]
