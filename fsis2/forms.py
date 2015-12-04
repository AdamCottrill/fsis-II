from django.contrib.gis import forms
from django.contrib.gis.forms.fields import PolygonField

from leaflet.forms.widgets import LeafletWidget

from fsis2.models import Species


class GeoForm(forms.Form):
    """Load a map centered over Lake Huron. """

    selection = forms.PolygonField(widget=LeafletWidget(),
                                   required=True)

    earliest = forms.CharField(label='Earliest Year', max_length=4,
                               required=False)
    latest = forms.CharField(label='Latest Year', max_length=4,
                             required=False)

    species = forms.ModelMultipleChoiceField(
        Species.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple(), label='Species')


    def clean_earliest(self):
        '''If we can't convert the earliest year value to an integer,
        throw an error'''
        yr =  self.cleaned_data['earliest']
        if yr:
            try:
                yr = int(yr)
            except ValueError:
                msg = "'Earliest Year' must be numeric."
                raise forms.ValidationError(msg.format())
            return yr
        else:
            return yr

    def clean_latest(self):
        '''If we can't convert the latest year value to an integer,
        throw an error'''
        yr =  self.cleaned_data['latest']
        if yr:
            try:
                yr = int(yr)
            except ValueError:
                msg = "'Latest Year' must be numeric."
                raise forms.ValidationError(msg.format())
            return yr
        else:
            return yr

    def clean(self):
        cleaned_data = super(GeoForm, self).clean()

        first_year = cleaned_data.get('earliest')
        last_year = cleaned_data.get('latest')

        if first_year and last_year:
            if first_year > last_year:
                msg = "'Earliest Year' occurs after 'Last Year'."
                raise forms.ValidationError(msg)
        return cleaned_data
