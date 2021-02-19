# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking_fields', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trackingevent',
            options={'verbose_name': 'Tracking event', 'ordering': ['-date'], 'verbose_name_plural': 'Tracking events'},
        ),
    ]
