# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Date')),
                ('action', models.CharField(verbose_name='Action', max_length=1, editable=False, choices=[(b'C', 'Create'), (b'U', 'Update'), (b'D', 'Delete')])),
                ('object_id', models.PositiveIntegerField(editable=False)),
                ('object_repr', models.CharField(help_text='Object reprensentation, useful if the object is deleted later.', verbose_name='Object', max_length=100, editable=False)),
                ('user_id', models.PositiveIntegerField(editable=False)),
                ('user_repr', models.CharField(help_text='User reprensentation, useful if the user is deleted later.', verbose_name='User', max_length=100, editable=False)),
                ('object_content_type', models.ForeignKey(related_name=b'tracking_object_content_type', editable=False, to='contenttypes.ContentType')),
                ('user_content_type', models.ForeignKey(related_name=b'tracking_user_content_type', editable=False, to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrackField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, verbose_name='Name')),
                ('old_value', models.TextField(verbose_name='Old value')),
                ('new_value', models.TextField(verbose_name='New value')),
                ('event', models.ForeignKey(verbose_name='Event', to='tracking_fields.TrackEvent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
