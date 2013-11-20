from django import forms
from olwidget.fields import MapField, EditableLayerField

##from crispy_forms.helper import FormHelper
##from crispy_forms.layout import Submit
##from crispy_forms.layout import Layout, Div

from fsis2.models import Species


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


    species = forms.ModelMultipleChoiceField(
        Species.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple(), label='Species')

    ##  helper = FormHelper()
    ##  helper.form_id = 'FindEventsMap'
    ##  helper.form_class = 'blueForms'
    ##  helper.form_method = 'post'
    ##  helper.form_action = ''
    ##  helper.add_input(Submit('submit', 'Submit'))
    ##  
    ##  helper.layout = Layout(
    ##      Div(
    ##          Div(selection, class_id='col-md-9'),
    ##          Div(species, class_id='col-md-3'),
    ##          class_id='row')
    ##  )