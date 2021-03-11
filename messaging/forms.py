from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

class UserMessageForm(forms.Form):
    message_content = forms.CharField(
        label=_("Envoyer un message"),
        widget=forms.Textarea(
            attrs={
                'class': "form-control", 
                'placeholder': _("Message"),
            }
        ),
        required=True,
        error_messages={
            'required': "Vous ne pouvez pas envoyer un message vide",
        }
    )
