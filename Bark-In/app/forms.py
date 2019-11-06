"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,UserChangeForm
from django.forms import ModelForm
from app.models import UserProfile
from django.utils.translation import ugettext_lazy as _

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class EditProfileForm(ModelForm):
    class Meta:
        model=User
        fields = (
            'username',
            'password',
            )
class ProfileForm(ModelForm):
         class Meta:
             model = UserProfile
             fields = ('bio', 'dogs')