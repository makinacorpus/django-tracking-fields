# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking_fields', '0002_auto_20141003_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackingevent',
            name='object_id',
            field=models.PositiveIntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='trackingevent',
            name='user_id',
            field=models.PositiveIntegerField(null=True, editable=False),
        ),
    ]
