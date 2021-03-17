from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class UserMessageForm(forms.Form):
    message_content = forms.CharField(
        label=_("Envoyer un message"),
        widget=forms.Textarea(
            attrs={
                'class': "form-control", 
                'placeholder': _("Message"),
                'rows': "3",
            }
        ),
        help_text=_("Vous pouvez envoyer votre message en appuyant sur SHIFT + ENTER"),
        required=False
    )

    def clean_message_content(self):
        content = self.cleaned_data.get('message_content')
        if (content == "" or content.strip() == ""):            
            raise ValidationError(
                message=_("Vous ne pouvez pas envoyer un message vide"),
                code="required"
            )
        return content
