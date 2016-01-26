# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.EmailField(unique=True, max_length=255)),
                ('email', models.EmailField(unique=True, verbose_name='email address', max_length=255)),
                ('first_name', models.CharField(null=True, blank=True, max_length=120)),
                ('last_name', models.CharField(null=True, blank=True, max_length=120)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_member', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
