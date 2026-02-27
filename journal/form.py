from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from django_registration.forms import RegistrationForm as DefaultRegistrationForm

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=255)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    captcha = CaptchaField()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        label="Old password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

class CustomRegistrationForm(DefaultRegistrationForm):
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field from the UI
        if 'username' in self.fields:
            del self.fields['username']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email:
            # Enforce email as username
            cleaned_data['username'] = email
            
            # Check for existing inactive user with this email/username to clean up
            if User.objects.filter(email__iexact=email, is_active=False).exists():
                User.objects.filter(email__iexact=email, is_active=False).delete()
            if User.objects.filter(username__iexact=email, is_active=False).exists():
                User.objects.filter(username__iexact=email, is_active=False).delete()
                
        return cleaned_data

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email).exists():
            raise ValidationError("We couldn't find an account with that email address.")
        return email
class ResendActivationForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=255)
    captcha = CaptchaField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email, is_active=False).exists():
            if User.objects.filter(email__iexact=email, is_active=True).exists():
                raise ValidationError("This account is already active. Please log in.")
            raise ValidationError("We couldn't find an inactive account with that email address.")
        return email

class VerificationCodeForm(forms.Form):
    code = forms.CharField(label='Verification Code', max_length=6, min_length=6, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456'}))
    captcha = CaptchaField()
