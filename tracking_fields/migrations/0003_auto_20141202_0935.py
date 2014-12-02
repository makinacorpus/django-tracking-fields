# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking_fields', '0002_auto_20141029_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackingevent',
            name='object_repr',
            field=models.CharField(help_text='Object representation, useful if the object is deleted later.', verbose_name='Object representation', max_length=250, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trackingevent',
            name='user_repr',
            field=models.CharField(help_text='User representation, useful if the user is deleted later.', verbose_name='User representation', max_length=250, editable=False),
            preserve_default=True,
        ),
    ]
