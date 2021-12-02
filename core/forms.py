from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['mutations', ]
        widgets = {
            'date_of_probe': forms.DateInput(attrs={'type': 'date'}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }
    mutations = forms.JSONField(widget=forms.HiddenInput(attrs={'id': 'mutations'}))
