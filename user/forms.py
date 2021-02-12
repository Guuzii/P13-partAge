from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    UserCreationForm, 
    UserChangeForm, 
    AuthenticationForm,
    UsernameField
)
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    first_name = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(
            attrs={
                'class': "form-control", 
                'placeholder': "Prénom",
            }
        ),
        required=True,
    )
    last_name = forms.CharField(
        label="Nom",
        widget=forms.TextInput(
            attrs={
                'class': "form-control", 
                'placeholder': "Nom",
            }
        ),
        required=True,
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                'class': "form-control", 
                'placeholder': "Email",
            }
        ),
        required=True,
    )
    birthdate = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(
            attrs={
                'class': "form-control", 
                'placeholder': "Date de naissance",
            },
        ),
        input_formats=[
            '%d-%m-%Y',
            '%d/%m/%Y',
        ],
        help_text="Saisissez une date au format 'JJ-MM-AAAA' ou 'JJ/MM/AAAA'",
        required=True,
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(
            attrs={
                'class': "form-control", 
                'placeholder': "Mot de passe",
            },
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=True,
    )
    password2 = forms.CharField(
        label='Confirmation du mot de passe', 
        widget=forms.PasswordInput(
            attrs={
                'class': "form-control", 
                'placeholder': "Confirmer mot de passe",
            },
        ),
        strip=False,
        help_text="Saisissez le même mot de passe que celui entré précedement",
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'birthdate',
        )
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Les mots de passe ne sont pas la mêmes"))
        return password2


class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'birthdate'
        )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CustomUserLoginForm(AuthenticationForm):
    username = UsernameField(
        label="Identifiant/Email",
        widget=forms.TextInput(
            attrs={
                'autofocus': False,
                'class': "form-control",
                'placeholder': "Identifiant",
            }
        ),
        required=True,
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={
                'class': "form-control", 
                'placeholder': "Mot de passe",
            }
        ),
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 
            'password'
        )
