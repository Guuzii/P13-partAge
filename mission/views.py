from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.utils.timezone import now

from mission.forms import CreateMissionForm

from mission.models.mission_status import MissionStatus
from mission.models.mission_category import MissionCategory
from mission.models.mission import Mission
from mission.models.mission_bonus_reward import MissionBonusReward

from messaging.forms import UserMessageForm

from messaging.models.message import UserMessage
from user.models.user_type import UserType
from user.models.custom_user import CustomUser


def get_mission_by_uid(uidb64):
    uidb64_split = uidb64.split('-')
    if (len(uidb64_split) > 1):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64_split[1]))
            mission = Mission.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Mission.DoesNotExist):
            mission = None
    else:
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            mission = Mission.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Mission.DoesNotExist):
            mission = None

    return mission

def get_acceptor_user_by_uid(uidb64):
    uidb64_split = uidb64.split('-')
    try:
        uid = force_text(urlsafe_base64_decode(uidb64_split[0]))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Mission.DoesNotExist):
        user = None

    return user

def init_mission_status():
    mission_status_open = MissionStatus.objects.get(label__iexact='open')
    mission_status_close = MissionStatus.objects.get(label__iexact='close')
    mission_status_finish = MissionStatus.objects.get(label__iexact='finish')
    return mission_status_open, mission_status_close, mission_status_finish

def init_user_type():
    senior_type = UserType.objects.get(label__iexact="senior")
    junior_type = UserType.objects.get(label__iexact="junior")
    return senior_type, junior_type


class MissionBoard(View):
    template_name = 'mission/board.html'
    context = {
        'title': _("TABLEAU DES MISSIONS"),
    }    

    def get(self, request):
        self.senior_type, self.junior_type = init_user_type()
        self.mission_status_open, self.mission_status_ongoing, self.mission_status_finish = init_mission_status()
        if (request.user.user_type not in [self.senior_type, self.junior_type]):
            messages.error(
                request, 
                message=_("Vous ne pouvez pas accéder aux missions car vous n'avez pas de type utilisateur défini"),
                extra_tags="alert-danger"
            )
            return redirect('home')

        if (request.GET.get('status')):
            mission_status = MissionStatus.objects.get(label__iexact=request.GET.get('status'))

            if (request.user.user_type == self.senior_type):
                missions = Mission.objects.filter(Q(bearer_user=request.user) & Q(status__pk=mission_status.pk))
            else:
                if (mission_status == self.mission_status_open):
                    missions = Mission.objects.filter(status__pk=self.mission_status_open.pk)
                else:
                    missions = Mission.objects.filter(Q(acceptor_user=request.user) & Q(status__pk=mission_status.pk))


            missions_with_uid = []
            for mission in missions:
                missions_with_uid.append({
                    'mission': serializers.serialize('json', (mission,)),
                    'uid': urlsafe_base64_encode(force_bytes(mission.pk))
                })

            request.session['mission_filter'] = request.GET.get('status')
            return JsonResponse(missions_with_uid, safe=False)                

        if (request.user.user_type == self.senior_type):
            self.context['senior'] = True
        else:
            self.context['senior'] = False

        status_filter = request.session.get('mission_filter')

        if (status_filter):
            mission_status = MissionStatus.objects.get(label__iexact=status_filter)
            if (request.user.user_type == self.senior_type):
                missions = Mission.objects.filter(Q(bearer_user=request.user) & Q(status__pk=mission_status.pk))
            else:
                if (mission_status == self.mission_status_open):
                    missions = Mission.objects.filter(status__pk=self.mission_status_open.pk)
                else:
                    missions = Mission.objects.filter(Q(acceptor_user=request.user) & Q(status__pk=mission_status.pk))
        else:
            if (request.user.user_type == self.senior_type):
                missions = Mission.objects.filter(Q(bearer_user=request.user) & Q(status__pk=self.mission_status_open.pk))
            else:
                missions = Mission.objects.filter(status__pk=self.mission_status_open.pk)

        missions_with_uid = []
        for mission in missions:
            missions_with_uid.append({
                'mission': mission,
                'uid': urlsafe_base64_encode(force_bytes(mission.pk))
            })
            
        self.context['missions'] = missions_with_uid

        return render(request, self.template_name, self.context)


class MissionDetails(View):
    template_name = 'mission/details.html'
    context = {
        'title': _("DETAILS"),
    }    

    def get(self, request, uidb64):
        self.senior_type, self.junior_type = init_user_type()
        mission_status_ongoing = MissionStatus.objects.get(label__iexact="ongoing")
        mission = get_mission_by_uid(uidb64)
        if mission is not None:
            if(request.GET.get('infos')):
                return JsonResponse(mission.pk, safe=False)
                
            self.context['mission'] = mission

            if (request.user.user_type == self.senior_type):
                # SENIOR   
                self.context['senior'] = True

                if (mission.status == mission_status_ongoing):
                    self.context['acceptor_user'] = mission.acceptor_user
                    self.context['uid'] = urlsafe_base64_encode(force_bytes(mission.acceptor_user.pk)) + "-" + urlsafe_base64_encode(force_bytes(mission.pk))
                
                    return render(request, self.template_name, self.context)

                receiver_user_messages_distinct = UserMessage.objects.filter(Q(receiver_user=request.user) & Q(mission=mission)).order_by('sender_user').distinct('sender_user')
                applicants = []

                for message in receiver_user_messages_distinct:
                    applicants.append(message.sender_user)

                applicants_with_uid = []

                for applicant in applicants:
                    bearer_respond = UserMessage.objects.filter(
                        Q(Q(sender_user=request.user) & Q(receiver_user=applicant)) &
                        Q(mission=mission)
                    ).exists()
                    uid = urlsafe_base64_encode(force_bytes(applicant.pk)) + "-" + urlsafe_base64_encode(force_bytes(mission.pk))
                    applicants_with_uid.append({
                        'user': applicant,
                        'uid': uid,
                        'bearer_respond': bearer_respond
                    })

                self.context['applicants'] = applicants_with_uid
                
                return render(request, self.template_name, self.context)
            elif (request.user.user_type == self.junior_type):
                # JUNIOR
                has_apply = UserMessage.objects.filter(Q(sender_user=request.user) & Q(mission=mission)).exists()
                self.context['senior'] = False
                self.context['uid'] = urlsafe_base64_encode(force_bytes(mission.bearer_user.pk)) + "-" + urlsafe_base64_encode(force_bytes(mission.pk))

                if (has_apply):
                    got_response = UserMessage.objects.filter(Q(receiver_user=request.user) & Q(mission=mission)).exists()
                    self.context['has_apply'] = has_apply
                    self.context['got_response'] = got_response
                else:
                    self.context['form'] = UserMessageForm()
                    self.context['form_id'] = "send-message-form"
                    self.context['form_action'] = "message-conv"
                    self.context['submit_button_label'] = _("Postuler")
                    self.context['back_url_name'] = "mission-board"
                
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
                message=_("Un problème est survenu au moment d'afficher les détails de la mission, la mission est inexistante"),
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

    def get(self, request):
        senior_type = UserType.objects.get(label__iexact="senior")
        if(request.user.user_type == senior_type):
            # if (request.GET.get('category_info')):
            #     mission_categories = MissionCategory.objects.all()
            #     categories_with_amount = []
            #     for category in mission_categories:
            #         categories_with_amount.append({
            #             'mission': serializers.serialize('json', (mission,)),
            #             'uid': urlsafe_base64_encode(force_bytes(mission.pk))
            #         })
            self.context['form'] = CreateMissionForm(user=request.user)
            return render(request, self.template_name, self.context)
        else:
            return redirect('mission-board')

    def post(self, request):
        senior_type = UserType.objects.get(label__iexact="senior")
        if(request.user.user_type == senior_type):
            form = CreateMissionForm(user=request.user, data=request.POST)

            if (form.is_valid()):
                category_reward_amount = form.cleaned_data.get('mission_category').base_reward_amount
                bonus_reward_amount = int(form.cleaned_data.get('mission_bonus_amount'))
                mission_total_reward_amount = category_reward_amount + bonus_reward_amount

                if (request.user.wallet.balance < mission_total_reward_amount):
                    self.context['form'] = form
                    self.context['errors'] = {
                        ('balance', "Vous n'avez pas les fonds disponibles pour créer cette mission"),
                    }

                    return render(request, self.template_name, self.context)                    

                bonus_description = form.cleaned_data.get('mission_bonus_description')
                if not bonus_description:
                    bonus_description = _("Un grand merci !")

                new_bonus_reward = MissionBonusReward(
                    reward_amount=bonus_reward_amount,
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
                    request.user.wallet.balance -= mission_total_reward_amount
                    request.user.wallet.save()
                    messages.success(
                        request, 
                        message=_("Mission créée avec succés. Elle sera disponible pour les utilisateurs une fois validée par un Administrateur"),
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


class MissionManagement(View):

    def post(self, request, uidb64):
        mission_status_ongoing = MissionStatus.objects.get(label__iexact="ongoing")
        mission_status_finish = MissionStatus.objects.get(label__iexact="finish")
        mission = get_mission_by_uid(uidb64)

        if (mission is not None ):
            if (request.POST.get('action') == "accept" and mission.status != mission_status_ongoing):
                acceptor_user = get_acceptor_user_by_uid(uidb64)
                mission.acceptor_user = acceptor_user
                mission.status = mission_status_ongoing
                mission.updated_at = now()
                mission.save()
                                
                messages.success(
                    request, 
                    message=_("Utilisateur {} {} accepté pour la mission".format(acceptor_user.first_name, acceptor_user.last_name)),
                    extra_tags="alert-success"
                )
            elif (request.POST.get('action') == "end" and mission.status == mission_status_ongoing):
                if (request.user == mission.bearer_user):
                    mission.bearer_validate = True
                else:
                    mission.acceptor_validate = True

                if (mission.bearer_validate and mission.acceptor_validate):
                    reward_receiver = CustomUser.objects.get(pk=mission.acceptor_user.pk)
                    reward_receiver.experience_point += mission.category.xp_amount
                    reward_receiver.wallet.balance += mission.category.base_reward_amount + mission.bonus_reward.reward_amount
                    reward_receiver.save()
                    reward_receiver.wallet.save()
                    mission.status = mission_status_finish            
                
                mission.updated_at = now()
                mission.save()
            else:                
                messages.error(
                    request, 
                    message=_("Action non comprise"),
                    extra_tags="alert-danger"
                )
            
            return redirect('mission-details', uidb64=urlsafe_base64_encode(force_bytes(mission.pk)))
        else:                
            messages.error(
                request, 
                message=_("Mission inexistante"),
                extra_tags="alert-danger"
            )
            return redirect('mission-board')
    
