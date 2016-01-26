# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Norification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('sender_object_id', models.PositiveIntegerField()),
                ('verb', models.CharField(max_length=255)),
                ('action_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('target_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action_content_type', models.ForeignKey(null=True, to='contenttypes.ContentType', related_name='notify_action', blank=True)),
                ('sender_content_type', models.ForeignKey(to='contenttypes.ContentType', related_name='notify_sender')),
                ('target_content_type', models.ForeignKey(null=True, to='contenttypes.ContentType', related_name='notify_target', blank=True)),
            ],
        ),
    ]
