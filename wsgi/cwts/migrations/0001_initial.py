# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fsis2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CWT',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stocked', models.BooleanField(default=True)),
                ('cwt', models.CharField(max_length=6)),
                ('seq_start', models.IntegerField(default=0)),
                ('seq_end', models.IntegerField(default=1)),
                ('tag_cnt', models.IntegerField(null=True, blank=True)),
                ('tag_type', models.IntegerField(default=6, choices=[(6, b'Coded Wire'), (17, b'Sequential CWT')])),
                ('cwt_mfr', models.CharField(max_length=10, choices=[(b'MM', b'Micro Mark'), (b'NMT', b'Northwest Marine Technologies')])),
                ('cwt_reused', models.BooleanField(default=False)),
                ('strain', models.CharField(blank=True, max_length=10, null=True, choices=[(b'BS', b'Big Sound'), (b'GL', b'Green Lake'), (b'IB', b'Iroquois Bay'), (b'JL', b'Jenny Lake'), (b'LL', b'Lewis Lake'), (b'LM', b'Lake Manitou'), (b'LO', b'Lake Ontario'), (b'MA', b'Marquette'), (b'MASE', b'Marquette cross'), (b'MP', b'Michipicoten Island'), (b'SA', b'Apositle Island'), (b'SI', b'Superior Isle Royal'), (b'SN', b'Seneca Lake'), (b'STI', b'Superior Traverse Island'), (b'WI', b'Wisconsin'), (b'MB', b'Mishubishu'), (b'ST', b'Slate Island'), (b'UNKN', b'Unknown')])),
                ('development_stage', models.IntegerField(default=99, null=True, blank=True, choices=[(99, b'Unknown'), (10, b'Egg (unknown stage)'), (12, b'Eyed Eggs'), (31, b'Fry (1-2 months)'), (32, b'Fingerling (3-9 months)'), (50, b'Juvenile / Adult (unknown age)'), (51, b'Yearling (10-19 months)'), (52, b'Sub-adult (>= 20 months, but immature)'), (53, b'Adult (mature)'), (81, b'Sac Fry (0-1 month)')])),
                ('year_class', models.IntegerField(null=True, blank=True)),
                ('stock_year', models.IntegerField(null=True, blank=True)),
                ('plant_site', models.CharField(max_length=80, null=True, blank=True)),
                ('release_basin', models.CharField(blank=True, max_length=6, null=True, choices=[(b'HU', b'Lake Huron'), (b'MI', b'Lake Michigan'), (b'SU', b'Lake Superior'), (b'ER', b'Lake Superior'), (b'MIHU', b'Lakes Huron and Michigan'), (b'MIHUSU', b'Lakes Huron, Michigan and Superior'), (b'UNKN', b'Unknown')])),
                ('us_grid_no', models.CharField(max_length=4, null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(help_text=b'Represented as (longitude, latitude)', srid=4326, null=True, blank=True)),
                ('ltrz', models.IntegerField(blank=True, null=True, choices=[(1, b'Western North Channel'), (2, b'Darch Islands'), (3, b'Fraser Bay'), (4, b'Grand Bank/Dawson Rock'), (5, b'Iroquois Bay'), (6, b'Parry Sound'), (7, b'Limestone Islands'), (8, b'Watcher Islands'), (9, b'Nottawasaga Bay'), (10, b'Owen Sound/Colpoys Bay'), (11, b'Point Clark'), (12, b'Western Bruce Penninsula'), (13, b'Bruce Archipelago'), (14, b'SW Manitoulin Island'), (15, b'South Bay'), (16, b'Six Fathom Bank'), (17, b'North Lake Huron Humps')])),
                ('hatchery', models.CharField(max_length=80, null=True, blank=True)),
                ('agency', models.CharField(max_length=5, choices=[(b'OMNR', b'Ontario Ministry of Natural Resources'), (b'MDNR', b'Michigan Department of Natural Resources'), (b'USFWS', b'U.S. Fish and Wildlife Service')])),
                ('comments', models.TextField(null=True, blank=True)),
                ('clipa', models.IntegerField(default=5, null=True, blank=True, choices=[(0, b'No Clip'), (1, b'Right Pectoral'), (2, b'Left Pectoral'), (3, b'Right Pelvic'), (4, b'Left Pelvic'), (14, b'Right Pectoral and Left Pelvic'), (23, b'Left Pectoral and Right Pelvic'), (5, b'Adipose')])),
                ('popup_text', models.CharField(max_length=5000)),
                ('spc', models.ForeignKey(blank=True, to='fsis2.Species', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CWT_recovery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cwt', models.CharField(max_length=6)),
                ('sequence_number', models.IntegerField(default=0)),
                ('recovery_source', models.CharField(max_length=20, choices=[(b'AOFRC', b'AOFRC'), (b'CF', b'Catch Sampling'), (b'CWT', b'CWT Cooperative'), (b'IA_Nearshore', b'Nearshore Index'), (b'IA_Offshore', b'Offshore Index'), (b'NAWASH', b'Nawash'), (b'SportCreel', b'Creels'), (b'SportFish', b'Sportfish')])),
                ('recovery_year', models.IntegerField()),
                ('recovery_date', models.DateField(null=True, blank=True)),
                ('recovery_grid', models.CharField(max_length=4)),
                ('composite_key', models.CharField(max_length=50)),
                ('flen', models.IntegerField(null=True, blank=True)),
                ('age', models.IntegerField(null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(help_text=b'Represented as (longitude, latitude)', srid=4326)),
                ('popup_text', models.CharField(max_length=2500)),
                ('spc', models.ForeignKey(to='fsis2.Species')),
            ],
        ),
    ]
