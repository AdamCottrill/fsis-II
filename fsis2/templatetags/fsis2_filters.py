from django import template
import datetime

register = template.Library()

@register.filter(name='format_ddlat')
def format_ddlat(x):
    try:
        d = int(x)
        m = (x-d)*60
        m = ("%.3f" % m).zfill(6)
        dd_lat = ''.join([str(d), "&#176;",m,"&#39; N"])
    except:
        dd_lat = x
    return dd_lat


@register.filter(name='format_ddlon', is_safe=True)
def format_ddlon(x):
    try:
        d = int(x)
        m = (x-d)*-60
        m = ("%.3f" % m).zfill(6)
        dd_lon = ''.join([str(d), "&#176;",m,"&#39; W"])
    except:
        dd_lon = x
    return dd_lon

@register.filter(name='format_cwt')
def format_cwt(x):
    '''format cwts as 63-03-99'''
    x = str(x)
    cwt = "-".join([x[:2], x[2:4], x[4:6]])
    return cwt


@register.filter(name='prj_cd_Year')
def prj_cd_Year(x):
    '''format LHA_IA12_000 as 2012'''
    if int(x[6:8]) > 60:
        yr = "19" + x[6:8]
    else:
        yr = "20" + x[6:8]
    return yr
