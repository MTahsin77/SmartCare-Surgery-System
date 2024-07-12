from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import UserProfile, GPDetails, PendingRegistration
from django.contrib.auth import login

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    specialty = forms.ChoiceField(choices=[('', 'Select Specialty')] + list(User.DOCTOR_SPECIALTIES), required=False)
    patient_type = forms.ChoiceField(choices=User.PATIENT_TYPE_CHOICES, required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control address-input'}), required=True)
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'date_of_birth', 
            'password1', 'password2', 'user_type', 'specialty', 'patient_type', 
            'address', 'latitude', 'longitude'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['specialty'].widget.attrs.update({'class': 'form-control specialty-field'})
        self.fields['patient_type'].widget.attrs.update({'class': 'form-control patient-type-field'})

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        specialty = cleaned_data.get('specialty')
        patient_type = cleaned_data.get('patient_type')

        if user_type == 'doctor' and not specialty:
            self.add_error('specialty', 'Specialty is required for doctors.')
        elif user_type == 'patient' and not patient_type:
            self.add_error('patient_type', 'Patient type is required for patients.')

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control address-input'}), required=True)
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    specialty = forms.ChoiceField(choices=[('', 'Select Specialty')] + list(User.DOCTOR_SPECIALTIES), required=False)

    class Meta:
        model = UserProfile
        fields = ['address', 'bio', 'latitude', 'longitude', 'specialty']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['date_of_birth'].initial = self.instance.user.date_of_birth
            self.fields['specialty'].initial = self.instance.user.specialty

        if self.instance and self.instance.user.user_type != 'doctor':
            del self.fields['specialty']

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        if 'specialty' in self.cleaned_data:
            user.specialty = self.cleaned_data['specialty']
        if commit:
            user.save()
            profile.save()
        return profile

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class CustomUserChangeForm(UserChangeForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    patient_type = forms.ChoiceField(choices=User.PATIENT_TYPE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'date_of_birth', 'user_type', 'phone_number', 'address', 'patient_type', 'specialty']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user_type != 'patient':
            del self.fields['patient_type']
        if self.instance.user_type != 'doctor':
            del self.fields['specialty']
class GPForm(forms.ModelForm):
    name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'id': 'address-input'}))
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = GPDetails
        fields = ['name', 'email', 'phone', 'address', 'latitude', 'longitude']

class DoctorSpecialtyFilterForm(forms.Form):
    specialty = forms.ChoiceField(choices=[('', 'All Specialties')] + list(User.DOCTOR_SPECIALTIES), required=False)

class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)


