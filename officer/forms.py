from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import OfficerProfile

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = OfficerProfile
        fields = ['profile_image']


class OfficerPasswordForm(PasswordChangeForm):
    pass
