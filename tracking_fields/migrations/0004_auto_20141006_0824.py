# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking_fields', '0003_auto_20141006_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackedfieldmodification',
            name='new_value',
            field=models.TextField(null=True, verbose_name='New value'),
        ),
        migrations.AlterField(
            model_name='trackedfieldmodification',
            name='old_value',
            field=models.TextField(null=True, verbose_name='Old value'),
        ),
    ]
