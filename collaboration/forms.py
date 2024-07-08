from django import forms
from .models import SharedPatientRecord, Message, TreatmentPlan, Referral
from .demo_data import DEMO_COLLABORATORS

class SharedPatientRecordForm(forms.ModelForm):
    shared_with = forms.MultipleChoiceField(
        choices=[(collab['email'], f"{collab['name']} - {collab['specialty']}") for collab in DEMO_COLLABORATORS],
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = SharedPatientRecord
        fields = ['shared_with']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

class TreatmentPlanForm(forms.ModelForm):
    class Meta:
        model = TreatmentPlan
        fields = ['title', 'description', 'collaborators']

class ReferralForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = ['referred_to', 'reason']