# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20150201_1004'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='purchase_confirmed',
            new_name='payment_confirmed',
        ),
    ]
