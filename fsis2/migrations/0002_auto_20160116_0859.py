# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsis2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cwts_applied',
            name='cwt',
            field=models.CharField(max_length=6, db_index=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='year',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='taggingevent',
            name='tag_type',
            field=models.IntegerField(default=6, db_index=True, choices=[(1, b'Streamer'), (2, b'Tubular Vinyl'), (5, b'Anchor'), (6, b'Coded Wire'), (17, b'Sequential_CWT')]),
        ),
    ]
