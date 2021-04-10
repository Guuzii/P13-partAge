from django import forms
from django.forms import ModelChoiceField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from mission.models.mission_category import MissionCategory
from mission.models.mission import Mission

from user.models.custom_user import CustomUser


class MissionCategoryModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} -- récompense de {} po".format(obj.label, obj.base_reward_amount)


class CreateMissionForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(CreateMissionForm, self).__init__(*args, **kwargs)
        self.request_user = CustomUser.objects.get(pk=user.pk)

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
        queryset=MissionCategory.objects.all().order_by('pk'),
        empty_label=None
    )
    mission_bonus_amount = forms.ChoiceField(        
        label=_("Montant récompense bonus"),
        widget=forms.Select(
            attrs={
                'class': "form-control",
            }
        ),
        choices=(
            (50, _("50 po")), 
            (100, _("100 po")), 
            (200, _("200 po")), 
            (400, _("400 po")),
        )
    )
    mission_bonus_description = forms.CharField(
        label=_("Description récompense bonus"),
        widget=forms.TextInput(
            attrs={
                'class': "form-control", 
                'placeholder': _("Un grand merci !"),
            }
        ),
        max_length=255,
        required=False
    )

    def clean_mission_title(self):
        title = self.cleaned_data.get('mission_title')
        if Mission.objects.filter(Q(bearer_user=self.request_user) & Q(title=title)).exists():
            raise ValidationError(
                "Vous ne pouvez pas créer deux missions avec le même titre",
                code="title",
                params={"title": title},
            )
        return title


