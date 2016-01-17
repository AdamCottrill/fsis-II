# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cwts', '0002_auto_20160114_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cwt',
            name='stock_year',
            field=models.IntegerField(db_index=True, null=True, blank=True),
        ),
    ]
