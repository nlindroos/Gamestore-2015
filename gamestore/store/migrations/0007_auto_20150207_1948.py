# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20150202_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='reference_number',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='ownedgame',
            unique_together=set([('player', 'game')]),
        ),
        migrations.AlterUniqueTogether(
            name='purchase',
            unique_together=set([('player', 'game')]),
        ),
    ]
