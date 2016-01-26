# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20151231_2120'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('bio', models.TextField(null=True, blank=True)),
                ('facebook_link', models.CharField(null=True, blank=True, verbose_name='Facebook profile url', max_length=320)),
                ('twitter_handle', models.CharField(null=True, blank=True, verbose_name='Twitter handle', max_length=320)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
