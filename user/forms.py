from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    UserCreationForm, 
    UserChangeForm, 
    AuthenticationForm,
    UsernameField,
    SetPasswordForm,
    PasswordResetForm
)
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from user.models.custom_user import CustomUser
from user.models.wallet import Wallet
from user.models.document import Document


def get_allowed_file_types(input_accept=False):
    if input_accept:
        accepted_types = ""
        for i, file_type in enumerate(settings.USER_FILE_ALLOWED_TYPES):
            if (i == 0):
                accepted_types += "." + file_type
            else:
                accepted_types += ", ." + file_type

        return accepted_types
    else:
        allowed_types = []
        for file_type in settings.USER_FILE_ALLOWED_TYPES:
            allowed_types.append("application/" + file_type)
            allowed_types.append("image/" + file_type)

        return allowed_types


class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    first_name = forms.CharField(
        label=_("Prénom"),
        widget=forms.TextInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Prénom"),
            }
        ),
        required=True,
    )
    last_name = forms.CharField(
        label=_("Nom"),
        widget=forms.TextInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Nom"),
            }
        ),
        required=True,
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Email"),
            }
        ),
        required=True,
    )
    birthdate = forms.DateField(
        label=_("Date de naissance"),
        widget=forms.DateInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Date de naissance"),
            },
        ),
        input_formats=[
            '%d-%m-%Y',
            '%d/%m/%Y',
        ],
        help_text=_("Saisissez une date au format 'JJ-MM-AAAA' ou 'JJ/MM/AAAA'"),
        required=True,
    )
    password1 = forms.CharField(
        label=_("Mot de passe"),
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Mot de passe"),
            },
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=True,
    )
    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Confirmer mot de passe"),
            },
        ),
        strip=False,
        help_text=_("Saisissez le même mot de passe que le précédent"),
        required=True,
    )
    file_identity = forms.FileField(
        label=_("Document d'identité"),
        widget=forms.FileInput(
            attrs={
                'class': "form-control",
                'accept': get_allowed_file_types(True),
            },
        ),
        error_messages={
            'required': "Vous devez fournir une copie de votre document d'identité (CNI/passeport)",
        }
    )
    file_criminal = forms.FileField(
        label=_("Casier judiciaire n°3"),
        widget=forms.FileInput(
            attrs={
                'class': "form-control",
                'accept': get_allowed_file_types(True),
            },
        ),
        error_messages={
            'required': "Vous devez fournir une copie de votre casier judiciaire n°3",
        }
    )    

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'birthdate',
        )

    def clean_email(self):
        # Check if email exists
        email = self.cleaned_data.get("email")     
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "Un utilisateur avec l'email %(email)s existe déjà.",
                code="email",
                params={"email": email},
            )
        return email
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Les mots de passe ne sont pas les mêmes"))
        return password2

    def clean_file_identity(self):
        # Check file type on identity document
        file_identity = self.cleaned_data.get('file_identity')
        content_type = file_identity.content_type
        allowed_types = get_allowed_file_types()

        if (content_type not in allowed_types):
            raise ValidationError(_("Le fichier d'identité doit être de type %s"%get_allowed_file_types(True)))

        return file_identity

    def clean_file_criminal(self):
        # Check file type on identity document
        file_criminal = self.cleaned_data.get('file_criminal')
        content_type = file_criminal.content_type
        allowed_types = get_allowed_file_types()

        if (content_type not in allowed_types):
            raise ValidationError(_("Le fichier casier judiciaire doit être de type %s"%get_allowed_file_types(True)))

        return file_criminal

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)

        if (user.is_admin == False):
            wallet = Wallet()
            wallet.save()
            user.wallet = wallet

        if commit:
            user.save()
        return user


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
            'birthdate',
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

    def clean_username(self):
        # Check if email exists
        email = self.cleaned_data.get("username")    
        if CustomUser.objects.filter(email__iexact=email).exists():
            user = CustomUser.objects.get(email__iexact=email)

            if not user.is_active:
                raise ValidationError(
                    _("Connexion impossible car ce compte n'est pas actif"),
                    code="inactive"
                )

        return email


class CustomUserPwdResetForm(SetPasswordForm):
    """Change password form."""    
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Mot de passe"),
            },
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=True,
    )

    new_password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Confirmer mot de passe"),
            },
        ),
        strip=False,
        help_text=_("Saisissez le même mot de passe que le précédent"),
        required=True,
    )

    def clean_new_password2(self):
        # Check that the two password entries match
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError(_("Les mots de passe ne sont pas les mêmes"))
        return new_password2


class CustomUserPwdForgotForm(PasswordResetForm):
    """User forgot password, check via email form."""
    email = forms.EmailField(
        label=_("Adresse email"),
        widget=forms.EmailInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Adresse email"),
            }
        ),
        required=True,
    )
