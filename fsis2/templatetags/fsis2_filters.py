from django import template


register = template.Library()

@register.filter(name='format_ddlat')
def format_ddlat(x):
    d = int(x)
    m = (x-d)*60
    m = ("%.3f" % m).zfill(6)
    dd_lat = ''.join([str(d), "&#176;",m,"&#39; N"])
    return dd_lat


@register.filter(name='format_ddlon', is_safe=True)
def format_ddlon(x):
    d = int(x)
    m = (x-d)*-60
    m = ("%.3f" % m).zfill(6)
    dd_lon = ''.join([str(d), "&#176;",m,"&#39; W"])
    return dd_lon
