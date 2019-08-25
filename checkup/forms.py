from checkup.models import *
from django import forms

# Create the form class.
class VisitleForm(forms.ModelForm):
     class Meta:
         model = Visit
         fields = '__all__'

class OneRoomForm(forms.ModelForm):
     class Meta:
         model = OnePeopleRoom
         fields = ['user1']

class TwoRoomForm(forms.ModelForm):
     class Meta:
         model = TwoPeopleRoom
         fields = ['user1','user2']

class ThreeRoomForm(forms.ModelForm):
     class Meta:
         model = ThreePeopleRoom
         fields = ['user1','user2','user3']

class FromToForm(forms.Form):
    start_date = forms.DateField(label='С')
    end_date = forms.DateField(label='До')
