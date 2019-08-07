from checkup.models import Visit
from django import forms

# Create the form class.
class VisitleForm(forms.ModelForm):
     class Meta:
         model = Visit
         fields = '__all__'

class FromToForm(forms.Form):
    start_date = forms.DateField(label='С')
    end_date = forms.DateField(label='До')
