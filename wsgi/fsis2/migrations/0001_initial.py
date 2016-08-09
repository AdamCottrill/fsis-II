# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BuildDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('build_date', models.DateField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='CWTs_Applied',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fs_tagging_event_id', models.IntegerField()),
                ('cwt', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prj_cd', models.CharField(max_length=13)),
                ('year', models.IntegerField()),
                ('fs_event', models.IntegerField(unique=True)),
                ('lotsam', models.CharField(max_length=8, null=True, blank=True)),
                ('event_date', models.DateTimeField(null=True, blank=True)),
                ('clipa', models.CharField(max_length=3, null=True, blank=True)),
                ('fish_age', models.IntegerField()),
                ('stkcnt', models.IntegerField()),
                ('fish_wt', models.FloatField(null=True, blank=True)),
                ('record_biomass_calc', models.FloatField(null=True, blank=True)),
                ('reartem', models.FloatField(null=True, blank=True)),
                ('sitem', models.FloatField(null=True, blank=True)),
                ('transit_mortality_count', models.IntegerField(null=True, blank=True)),
                ('dd_lat', models.FloatField()),
                ('dd_lon', models.FloatField()),
                ('geom', django.contrib.gis.db.models.fields.PointField(help_text=b'Represented as (longitude, latitude)', srid=4326)),
                ('popup_text', models.CharField(max_length=1500)),
                ('development_stage', models.IntegerField(default=99, choices=[(99, b'Unknown'), (10, b'Egg (unknown stage)'), (12, b'Eyed Eggs'), (31, b'Fry (1-2 months)'), (32, b'Fingerling (3-9 months)'), (50, b'Juvenile / Adult (unknown age)'), (51, b'Yearling (10-19 months)'), (52, b'Sub-adult (>= 20 months, but immature)'), (53, b'Adult (mature)'), (81, b'Sac Fry (0-1 month)')])),
                ('transit', models.CharField(default=b'UNKNOWN', max_length=20, null=True, blank=True, choices=[(b'ATV', b'All-terrain vehicle'), (b'BOAT', b'Boat'), (b'PLANE', b'Fixed wing Airplane'), (b'TUG', b'Great Lakes Tug'), (b'HELICOPTER', b'Helicopter'), (b'INCUBATOR', b'In-stream incubation'), (b'BACKPACK', b'Personal backpack'), (b'SNOWMOBILE', b'Snowmobile'), (b'TRUCK', b'Truck'), (b'UNKNOWN', b'Unknown')])),
                ('stocking_method', models.CharField(default=b'UNKNOWN', max_length=20, null=True, blank=True, choices=[(b'AERIAL DROP', b'Areal Drop'), (b'ICE', b'Under Ice'), (b'SUBMERGED', b'Submerged'), (b'SUBSURFACE', b'Subsurface'), (b'SURFACE', b'surface'), (b'UNKNOWN', b'Unknown')])),
                ('stocking_purpose', models.CharField(default=b'UNKNOWN', max_length=4, null=True, blank=True, choices=[(b'UNKN', b'Unknown'), (b'A', b'Rehabilitation'), (b'AC', b'Rehabilitation/Supplemental'), (b'AD', b'Rehabilitation/Research'), (b'AE', b'Rehabilitation/Assessment'), (b'B', b'Introduction'), (b'C', b'Supplemental'), (b'D', b'Research'), (b'DI', b'Research/Re-Introduction'), (b'EG', b'Assessment/Put-Grow-and-Take'), (b'EI', b'Assessment/Re-introduction'), (b'F', b'Put-and-Take'), (b'G', b'Put-Grow-and Take'), (b'I', b'Re-introduction')])),
            ],
            options={
                'ordering': ['-event_date'],
            },
        ),
        migrations.CreateModel(
            name='Lake',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lake', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Lake',
            },
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fs_lot', models.CharField(max_length=10)),
                ('spawn_year', models.IntegerField()),
                ('rearloc', models.CharField(max_length=30)),
                ('rearloc_nm', models.CharField(max_length=30)),
                ('proponent_type', models.CharField(default=b'OMNR', max_length=10, choices=[(b'CFIP', b'CFIP'), (b'OMNR', b'OMNR'), (b'PRIVATE', b'Private Hatchery'), (b'UNKNOWN', b'Unknown')])),
            ],
            options={
                'ordering': ['-spawn_year'],
            },
        ),
        migrations.CreateModel(
            name='ManagementUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=25)),
                ('slug', models.SlugField(unique=True, editable=False, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('mu_type', models.CharField(default=b'qma', max_length=10, choices=[(b'ltrz', b'Lake Trout Rehabilitation Zone'), (b'qma', b'Quota Management Area')])),
                ('lake', models.ForeignKey(default=1, to='fsis2.Lake')),
            ],
            options={
                'ordering': ['mu_type', 'label'],
            },
        ),
        migrations.CreateModel(
            name='Proponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbrev', models.CharField(unique=True, max_length=7)),
                ('proponent_name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['proponent_name'],
            },
        ),
        migrations.CreateModel(
            name='Readme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(editable=False)),
                ('comment', models.TextField()),
                ('initials', models.CharField(max_length=4)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('species_code', models.IntegerField(unique=True)),
                ('common_name', models.CharField(max_length=30)),
                ('scientific_name', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
                'ordering': ['species_code'],
            },
        ),
        migrations.CreateModel(
            name='StockingSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fsis_site_id', models.IntegerField(unique=True)),
                ('site_name', models.CharField(max_length=50)),
                ('stkwby', models.CharField(max_length=30)),
                ('stkwby_lid', models.CharField(max_length=15)),
                ('utm', models.CharField(max_length=20)),
                ('grid', models.CharField(max_length=4)),
                ('dd_lat', models.FloatField()),
                ('dd_lon', models.FloatField()),
                ('basin', models.CharField(max_length=15)),
                ('deswby_lid', models.CharField(max_length=30)),
                ('deswby', models.CharField(max_length=30)),
                ('popup_text', models.CharField(max_length=1500)),
                ('geom', django.contrib.gis.db.models.fields.PointField(help_text=b'Represented as (longitude, latitude)', srid=4326)),
            ],
            options={
                'ordering': ['site_name'],
            },
        ),
        migrations.CreateModel(
            name='Strain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sto_code', models.CharField(max_length=5)),
                ('strain_code', models.CharField(max_length=5)),
                ('strain_name', models.CharField(max_length=20)),
                ('species', models.ForeignKey(to='fsis2.Species')),
            ],
            options={
                'ordering': ['species', 'strain_name'],
            },
        ),
        migrations.CreateModel(
            name='TaggingEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fs_tagging_event_id', models.IntegerField(unique=True)),
                ('retention_rate_pct', models.FloatField(null=True, blank=True)),
                ('retention_rate_sample_size', models.IntegerField(null=True, blank=True)),
                ('retention_rate_pop_size', models.IntegerField(null=True, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('tag_type', models.IntegerField(default=6, choices=[(1, b'Streamer'), (2, b'Tubular Vinyl'), (5, b'Anchor'), (6, b'Coded Wire'), (17, b'Sequential_CWT')])),
                ('tag_position', models.IntegerField(default=4, choices=[(1, b'Flesh of Back'), (2, b'Operculum'), (3, b'Posterior Dorsal Fins'), (4, b'Snout')])),
                ('tag_origins', models.CharField(default=b'MNR', max_length=3, choices=[(b'CFP', b'Community Fisheries Involvement Program(CFIP)'), (b'MNR', b'Ontario Ministry of Natural Resources')])),
                ('tag_colour', models.CharField(default=b'NON', max_length=3, choices=[(b'BLK', b'Black'), (b'BLU', b'Blue'), (b'GRN', b'Green'), (b'NON', b'Colourless'), (b'OTH', b'Other'), (b'UNK', b'Unknown'), (b'YEL', b'Yellow')])),
                ('stocking_event', models.ForeignKey(to='fsis2.Event')),
            ],
        ),
        migrations.AddField(
            model_name='lot',
            name='proponent',
            field=models.ForeignKey(to='fsis2.Proponent'),
        ),
        migrations.AddField(
            model_name='lot',
            name='species',
            field=models.ForeignKey(to='fsis2.Species'),
        ),
        migrations.AddField(
            model_name='lot',
            name='strain',
            field=models.ForeignKey(to='fsis2.Strain'),
        ),
        migrations.AddField(
            model_name='event',
            name='lot',
            field=models.ForeignKey(to='fsis2.Lot'),
        ),
        migrations.AddField(
            model_name='event',
            name='site',
            field=models.ForeignKey(to='fsis2.StockingSite'),
        ),
        migrations.AddField(
            model_name='cwts_applied',
            name='tagging_event',
            field=models.ForeignKey(to='fsis2.TaggingEvent'),
        ),
    ]
