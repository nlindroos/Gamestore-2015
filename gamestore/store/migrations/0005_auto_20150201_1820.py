# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_remove_ownedgame_license_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='img_url',
            field=models.URLField(null=True, blank=True, default='store/images/russia.jpeg'),
            preserve_default=True,
        ),
    ]
