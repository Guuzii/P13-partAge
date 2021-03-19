from django import forms
from django.forms import ModelChoiceField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from mission.models.mission_category import MissionCategory


class MissionCategoryModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} -- récompense de {} po".format(obj.label, obj.base_reward_amount)


class CreateMissionForm(forms.Form):
    mission_title = forms.CharField(
        label=_("Titre de la mission"),
        widget=forms.TextInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Titre"),
            }
        ),
        max_length=50
    )
    mission_description = forms.CharField(
        label=_("Description de la mission"),
        widget=forms.Textarea(
            attrs={
                'class': "form-control", 
                'placeholder': _("Description"),
            }
        ),
    )
    mission_category = MissionCategoryModelChoiceField(
        label=_("Categorie de la mission"),
        widget=forms.Select(
            attrs={
                'class': "form-control",
            }
        ),
        queryset=MissionCategory.objects.all()
    )
    mission_bonus_amount = forms.ChoiceField(        
        label=_("Montant récompense bonus"),
        widget=forms.Select(
            attrs={
                'class': "form-control",
            }
        ),
        choices=(
            (10, _("10 po")), 
            (20, _("20 po")), 
            (50, _("50 po")), 
            (100, _("100 po")),
        )
    )
    mission_bonus_description = forms.CharField(
        label=_("Description récompense bonus"),
        widget=forms.TextInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Description"),
            }
        ),
        max_length=255,
        required=False
    )
