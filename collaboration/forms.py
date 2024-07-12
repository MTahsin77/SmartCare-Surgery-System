from django import forms
from .models import SharedPatientRecord
from .demo_data import DEMO_COLLABORATORS

class SharedPatientRecordForm(forms.ModelForm):
    shared_with = forms.MultipleChoiceField(
        choices=[(collab['email'], f"{collab['name']} - {collab['specialty']}") for collab in DEMO_COLLABORATORS],
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = SharedPatientRecord
        fields = ['shared_with']
