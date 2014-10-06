# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackedFieldModification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(verbose_name='Field', max_length=40, editable=False)),
                ('old_value', models.TextField(help_text=b'JSON serialized', verbose_name='Old value', null=True, editable=False)),
                ('new_value', models.TextField(help_text=b'JSON serialized', verbose_name='New value', null=True, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrackingEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('action', models.CharField(verbose_name='Action', max_length=6, editable=False, choices=[(b'CREATE', 'Create'), (b'UPDATE', 'Update'), (b'DELETE', 'Delete'), (b'ADD', 'Add'), (b'REMOVE', 'Remove'), (b'CLEAR', 'Clear')])),
                ('object_id', models.PositiveIntegerField(null=True, editable=False)),
                ('object_repr', models.CharField(help_text='Object reprensentation, useful if the object is deleted later.', verbose_name='Object representation', max_length=100, editable=False)),
                ('user_id', models.PositiveIntegerField(null=True, editable=False)),
                ('user_repr', models.CharField(help_text='User reprensentation, useful if the user is deleted later.', verbose_name='User representation', max_length=100, editable=False)),
                ('object_content_type', models.ForeignKey(related_name=b'tracking_object_content_type', editable=False, to='contenttypes.ContentType')),
                ('user_content_type', models.ForeignKey(related_name=b'tracking_user_content_type', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='trackedfieldmodification',
            name='event',
            field=models.ForeignKey(related_name=b'fields', editable=False, to='tracking_fields.TrackingEvent', verbose_name='Event'),
            preserve_default=True,
        ),
    ]
