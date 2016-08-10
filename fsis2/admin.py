from django.contrib import admin
from fsis2.models import Lot, Event, Species, Strain, Proponent

class LotAdmin(admin.ModelAdmin):
    pass

class EventAdmin(admin.ModelAdmin):
    pass

class SpeciesAdmin(admin.ModelAdmin):
    pass

class StrainAdmin(admin.ModelAdmin):
    pass

class ProponentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Lot, LotAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(Strain, StrainAdmin)
admin.site.register(Proponent, ProponentAdmin)
