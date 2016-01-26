# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('sender_object_id', models.PositiveIntegerField()),
                ('verb', models.CharField(max_length=255)),
                ('action_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('target_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action_content_type', models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType', related_name='notify_action')),
                ('sender_content_type', models.ForeignKey(to='contenttypes.ContentType', related_name='notify_sender')),
                ('target_content_type', models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType', related_name='notify_target')),
            ],
        ),
        migrations.RemoveField(
            model_name='norification',
            name='action_content_type',
        ),
        migrations.RemoveField(
            model_name='norification',
            name='sender_content_type',
        ),
        migrations.RemoveField(
            model_name='norification',
            name='target_content_type',
        ),
        migrations.DeleteModel(
            name='Norification',
        ),
    ]
