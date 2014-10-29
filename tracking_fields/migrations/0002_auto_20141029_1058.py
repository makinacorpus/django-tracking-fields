# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking_fields', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trackedfieldmodification',
            options={'verbose_name': 'Tracking field modification', 'verbose_name_plural': 'Tracking field modifications'},
        ),
        migrations.AlterModelOptions(
            name='trackingevent',
            options={'verbose_name': 'Tracking event', 'verbose_name_plural': 'Tracking events'},
        ),
        migrations.AlterField(
            model_name='trackingevent',
            name='object_repr',
            field=models.CharField(help_text='Object representation, useful if the object is deleted later.', verbose_name='Object representation', max_length=100, editable=False),
        ),
        migrations.AlterField(
            model_name='trackingevent',
            name='user_repr',
            field=models.CharField(help_text='User representation, useful if the user is deleted later.', verbose_name='User representation', max_length=100, editable=False),
        ),
    ]
