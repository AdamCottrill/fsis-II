from django import forms
from olwidget.fields import MapField, EditableLayerField

#from fsis.models import *


class GeoForm(forms.Form):
    """Load a map centered over Lake Huron. """

    selection = MapField([
        EditableLayerField({
            'geometry': 'polygon',
            'is_collection': False,
            #'name': 'selection',
        })],

         options= {
             'default_lat': 45,
             'default_lon': -81.7,
             'default_zoom':7,
             'map_div_style': {'width': '600px', 'height': '500px'},
          }

        )

