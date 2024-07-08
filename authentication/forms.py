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

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2', 'user_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = form.cleaned_data.get('user_type')
            
            if user_type in ['doctor', 'nurse', 'admin']:
                user.is_active = False
                user.save()
                PendingRegistration.objects.create(user=user)
                messages.info(request, 'Your registration is pending admin approval. You will be notified once approved.')
                return redirect('login')
            else:
                user.save()
                login(request, user)
                messages.success(request, f'Account created for {user.username}. You are now logged in.')
                return redirect('patient_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['address'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'address']

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
