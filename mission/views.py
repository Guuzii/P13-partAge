from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from mission.forms import CreateMissionForm

from mission.models.mission_status import MissionStatus
from mission.models.mission_category import MissionCategory
from mission.models.mission import Mission
from mission.models.mission_bonus_reward import MissionBonusReward

from messaging.forms import UserMessageForm

from messaging.models.message import UserMessage
from user.models.user_type import UserType


def get_mission_by_uid(uidb64):    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        mission = Mission.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Mission.DoesNotExist):
        mission = None

    return mission


class MissionBoard(View):
    context = {
        'title': _("TABLEAU DES MISSIONS"),
    }
    senior_type = UserType.objects.get(label__iexact="senior")
    junior_type = UserType.objects.get(label__iexact="junior")

    def get(self, request):
        if (request.user.user_type == self.senior_type):
            # SENIOR
            missions = Mission.objects.filter(bearer_user=request.user)

            missions_with_uid = []
            for mission in missions:
                missions_with_uid.append({
                    'mission': mission,
                    'uid': urlsafe_base64_encode(force_bytes(mission.pk))
                })
            
            self.template_name = 'mission/board_senior.html'
            self.context['missions'] = missions_with_uid

            return render(request, self.template_name, self.context)
        elif (request.user.user_type == self.junior_type):
            # JUNIOR
            self.template_name = 'mission/board_junior.html'

            return render(request, self.template_name, self.context)
        else:
            messages.error(
                request, 
                message=_("Vous ne pouvez pas accéder aux missions car vous n'avez pas de type utilisateur défini"),
                extra_tags="alert-danger"
            )
            return redirect('home')


class MissionDetails(View):
    template_name = 'mission/details.html'
    context = {
        'title': _("DETAILS"),
    }
    senior_type = UserType.objects.get(label__iexact="senior")
    junior_type = UserType.objects.get(label__iexact="junior")

    def get(self, request, uidb64):
        mission = get_mission_by_uid(uidb64)
        if mission is not None:
            if(request.GET.get('infos')):
                return JsonResponse(mission.pk, safe=False)
                
            self.context['mission'] = mission

            if (request.user.user_type == self.senior_type):
                # SENIOR
                receiver_user_messages_distinct = UserMessage.objects.filter(Q(receiver_user=request.user) & Q(mission=mission)).order_by('sender_user').distinct('sender_user')
                applicants = []

                for message in receiver_user_messages_distinct:
                    applicants.append(message.sender_user)

                applicants_with_uid = []

                for applicant in applicants:
                    applicants_with_uid.append({
                        'user': applicant,
                        'uid': urlsafe_base64_encode(force_bytes(applicant.pk)),
                    })
                
                self.context['senior'] = True
                self.context['applicants'] = applicants_with_uid
                
                return render(request, self.template_name, self.context)
            elif (request.user.user_type == self.junior_type):
                # JUNIOR
                self.context['senior'] = False
                self.context['form'] = UserMessageForm()
                self.context['form_id'] = "send-message-form"
                self.context['form_action'] = "message-conv"
                self.context['submit_button_label'] = _("Postuler")
                self.context['back_url_name'] = "mission-board"
                self.context['uid'] = uidb64
                
                return render(request, self.template_name, self.context)
            else:
                messages.error(
                    request, 
                    message=_("Vous ne pouvez pas accéder aux détails de la mission car vous n'avez pas de type utilisateur défini"),
                    extra_tags="alert-danger"
                )
                return redirect('home')
        else:                
            messages.error(
                request, 
                message=_("Un problème est survenu au moment d'afficher les détails de la mission"),
                extra_tags="alert-danger"
            )
            return redirect('mission-board')
    


class MissionCreate(View):
    template_name = 'mission/create.html'
    context = {
        'title': _("CREATION"),
        'form_id': "create-mission-form",
        'form_action': 'mission-create',
        'submit_button_label': _("Créer mission"),
    }
    senior_type = UserType.objects.get(label__iexact="senior")

    def get(self, request):
        if(request.user.user_type == self.senior_type):
            self.context['form'] = CreateMissionForm(user=request.user)
            return render(request, self.template_name, self.context)
        else:
            return redirect('mission-board')

    def post(self, request):
        if(request.user.user_type.pk == self.senior_type.pk):
            form = CreateMissionForm(user=request.user, data=request.POST)

            if (form.is_valid()):
                bonus_description = form.cleaned_data.get('mission_bonus_description')
                if not bonus_description:
                    bonus_description = _("Un grand merci !")

                new_bonus_reward = MissionBonusReward(
                    reward_amount=int(form.cleaned_data.get('mission_bonus_amount')),
                    description=bonus_description
                )
                new_bonus_reward.save()
                
                status_close = MissionStatus.objects.get(label__iexact="close")
                new_mission = Mission(
                    bearer_user=request.user,
                    status=status_close,
                    category=form.cleaned_data.get('mission_category'),
                    bonus_reward=new_bonus_reward,
                    title=form.cleaned_data.get('mission_title'),
                    description=form.cleaned_data.get('mission_description')
                )
                new_mission.save()

                if (new_mission.pk is None):
                    created = False
                else:
                    if (Mission.objects.filter(pk=new_mission.pk).exists()):
                        created = True
                    else:
                        created = False

                if (created):
                    messages.success(
                        request, 
                        message=_("Mission créée avec succés. Elle sera disponible pour les utilisateurs unefois validée par un Administrateur"),
                        extra_tags="alert-success"
                    )
                else:
                    messages.error(
                        request, 
                        message=_("Erreur lors de la création de la mission"),
                        extra_tags="alert-danger"
                    )

                return redirect('mission-board')
            else:                
                self.context['form'] = form
                self.context['errors'] = form.errors.items()
                return render(request, self.template_name, self.context)
        else:
            return redirect('mission-board')
