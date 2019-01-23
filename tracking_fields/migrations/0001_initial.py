# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackedFieldModification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('field', models.CharField(verbose_name='Field', max_length=40, editable=False)),
                ('old_value', models.TextField(help_text='JSON serialized', verbose_name='Old value', null=True, editable=False)),
                ('new_value', models.TextField(help_text='JSON serialized', verbose_name='New value', null=True, editable=False)),
            ],
            options={
                'verbose_name': 'Tracking field modification',
                'verbose_name_plural': 'Tracking field modifications',
            },
        ),
        migrations.CreateModel(
            name='TrackingEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('action', models.CharField(verbose_name='Action', max_length=6, editable=False, choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'), ('ADD', 'Add'), ('REMOVE', 'Remove'), ('CLEAR', 'Clear')])),
                ('object_id', models.PositiveIntegerField(null=True, editable=False)),
                ('object_repr', models.CharField(help_text='Object representation, useful if the object is deleted later.', verbose_name='Object representation', max_length=250, editable=False)),
                ('user_id', models.PositiveIntegerField(null=True, editable=False)),
                ('user_repr', models.CharField(help_text='User representation, useful if the user is deleted later.', verbose_name='User representation', max_length=250, editable=False)),
                ('object_content_type', models.ForeignKey(related_name='tracking_object_content_type', editable=False, to='contenttypes.ContentType', on_delete=models.CASCADE)),
                ('user_content_type', models.ForeignKey(related_name='tracking_user_content_type', editable=False, to='contenttypes.ContentType', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Tracking event',
                'verbose_name_plural': 'Tracking events',
            },
        ),
        migrations.AddField(
            model_name='trackedfieldmodification',
            name='event',
            field=models.ForeignKey(related_name='fields', editable=False, to='tracking_fields.TrackingEvent', verbose_name='Event', on_delete=models.CASCADE),
        ),
    ]
