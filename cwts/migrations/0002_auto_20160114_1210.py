# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cwts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cwt',
            name='cwt',
            field=models.CharField(max_length=6, db_index=True),
        ),
        migrations.AlterField(
            model_name='cwt_recovery',
            name='cwt',
            field=models.CharField(max_length=6, db_index=True),
        ),
        migrations.AlterField(
            model_name='cwt_recovery',
            name='recovery_year',
            field=models.IntegerField(db_index=True),
        ),
    ]
