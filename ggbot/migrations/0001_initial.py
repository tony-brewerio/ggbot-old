# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-15 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ip', models.GenericIPAddressField()),
            ],
            options={
                'db_table': 'ggbot_room',
            },
        ),
    ]
