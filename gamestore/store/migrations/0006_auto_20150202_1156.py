# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_auto_20150201_1820'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='highscore',
            unique_together=set([('player', 'game')]),
        ),
    ]
