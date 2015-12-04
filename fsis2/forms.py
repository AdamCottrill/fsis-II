from django.contrib.gis import forms
from django.contrib.gis.forms.fields import PolygonField

from leaflet.forms.widgets import LeafletWidget

from fsis2.models import Species


class GeoForm(forms.Form):
    """Load a map centered over Lake Huron. """

    selection = forms.PolygonField(widget=LeafletWidget())

    species = forms.ModelMultipleChoiceField(
        Species.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple(), label='Species')
