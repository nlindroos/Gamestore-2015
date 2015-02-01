# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='highscore',
            options={'ordering': ['game', '-score', 'date_time', 'player']},
        ),
        migrations.AddField(
            model_name='game',
            name='description',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='game',
            name='img_url',
            field=models.URLField(blank=True, null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ownedgame',
            name='license_active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='purchase',
            name='purchase_confirmed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='game',
            name='price',
            field=models.DecimalField(decimal_places=2, validators=[store.models.validate_price], max_digits=5, default=0.0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='game',
            name='tags',
            field=models.TextField(blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='game',
            name='url',
            field=models.URLField(default='http://example.com'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='purchase',
            name='fee',
            field=models.DecimalField(decimal_places=2, max_digits=5, default=0.0),
            preserve_default=True,
        ),
    ]
