# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20150201_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ownedgame',
            name='license_active',
        ),
    ]
