# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=60)),
                ('url', models.URLField()),
                ('price', models.DecimalField(max_digits=5, decimal_places=2)),
                ('tags', models.TextField()),
                ('developer', models.ForeignKey(to='store.Developer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Highscore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('score', models.DecimalField(max_digits=11, decimal_places=2)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(to='store.Game')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OwnedGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('game_state', models.TextField()),
                ('game', models.ForeignKey(to='store.Game')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('fee', models.DecimalField(max_digits=5, decimal_places=2)),
                ('game', models.ForeignKey(to='store.Game')),
                ('player', models.ForeignKey(to='store.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ownedgame',
            name='player',
            field=models.ForeignKey(to='store.Player'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='highscore',
            name='player',
            field=models.ForeignKey(to='store.Player'),
            preserve_default=True,
        ),
    ]
