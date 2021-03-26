from django.core import serializers
from django.shortcuts import render, redirect, reverse, get_object_or_404, get_list_or_404
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from messaging.forms import UserMessageForm

from messaging.models.message import UserMessage
from messaging.models.message_status import UserMessageStatus

from user.models.custom_user import CustomUser
from mission.models.mission_status import MissionStatus
from mission.models.mission import Mission


def get_user_by_uid(uidb64):
    uidb64_split = uidb64.split('-')
    try:
        user_uid = force_text(urlsafe_base64_decode(uidb64_split[0]))
        user = CustomUser.objects.get(pk=user_uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    return user

def get_mission_by_uid(uidb64):
    uidb64_split = uidb64.split('-')
    try:
        mission_uid = force_text(urlsafe_base64_decode(uidb64_split[1]))
        mission = Mission.objects.get(pk=mission_uid)
    except (TypeError, ValueError, OverflowError, Mission.DoesNotExist):
        mission = None

    return mission

def get_conversation_messages(auth_user, related_user, mission=None):
    if (mission):
        conversation_messages = UserMessage.objects.filter(
            Q(Q(sender_user=auth_user) & Q(receiver_user=related_user) & Q(mission__pk=mission.pk)) |
            Q(Q(sender_user=related_user) & Q(receiver_user=auth_user) & Q(mission__pk=mission.pk))
        ).order_by('created_at')
    else:
        conversation_messages = UserMessage.objects.filter(
            Q(Q(sender_user=auth_user) & Q(receiver_user=related_user)) |
            Q(Q(sender_user=related_user) & Q(receiver_user=auth_user))
        ).order_by('created_at')

    return conversation_messages

def get_conversation_messages_unviewed(auth_user, related_user, mission=None):    
    if (mission):
        conversation_messages_unviewed = UserMessage.objects.filter(
            Q(Q(sender_user=related_user) & Q(receiver_user=auth_user) & Q(mission__pk=mission.pk)) & 
            Q(is_viewed=False)
        ).order_by('created_at')
    else:
        conversation_messages_unviewed = UserMessage.objects.filter(
            Q(Q(sender_user=related_user) & Q(receiver_user=auth_user)) & 
            Q(is_viewed=False)
        ).order_by('created_at')

    return conversation_messages_unviewed


class MessageInbox(View):
    template_name = 'messaging/inbox.html'
    context = {
        'title': _("BOITE DE RECEPTION"),
    }
    mission_status_close = MissionStatus.objects.get(label__iexact='close')
    mission_status_finish = MissionStatus.objects.get(label__iexact='finish')

    def get(self, request):
        receiver_user_messages_distinct = UserMessage.objects.filter(receiver_user=request.user).exclude(
            Q(mission__status=self.mission_status_close) | Q(mission__status=self.mission_status_finish)
        ).order_by('sender_user').distinct('sender_user')
        related_users = []

        for message in receiver_user_messages_distinct:
            related_users.append({
                'user': message.sender_user,
                'mission': message.mission
            })

        related_users_with_uid = []

        for obj in related_users:
            uidb64 = urlsafe_base64_encode(force_bytes(obj['user'].pk)) + "-" + urlsafe_base64_encode(force_bytes(obj['mission'].pk))
            unreads = False
            unread_messages = get_conversation_messages_unviewed(request.user, obj['user'], obj['mission'])
            if (len(unread_messages) > 0):
                unreads = True

            related_users_with_uid.append({
                'user': obj['user'],
                'uid': uidb64,
                'unreads': unreads
            })
        
        self.context['related_users'] = related_users_with_uid
        return render(request, self.template_name, self.context)


class MessageConversation(View):
    template_name = 'messaging/conversation.html'
    context = {
        'title': _("CONVERSATION"),
        'form_id': "send-message-form",
        'form_action': 'message-conv',
        'submit_button_label': _("Envoyer"),
        'back_url_name': 'message-inbox'
    }
    mission_status_close = MissionStatus.objects.get(label__iexact='close')
    mission_status_finish = MissionStatus.objects.get(label__iexact='finish')

    def get(self, request, uidb64):
        self.context['errors'] = None
        related_user = get_user_by_uid(uidb64)
        mission = get_mission_by_uid(uidb64)

        if (related_user is not None and (mission.status != self.mission_status_finish or mission.status != self.mission_status_close)):
            if(request.GET.get('infos')):
                created_status = UserMessageStatus.objects.get(label="created")
                return JsonResponse({
                    'status_created_id': created_status.pk,
                    'user': {
                        'id': request.user.pk,
                        'fullname': request.user.first_name + " " + request.user.last_name
                    },
                    'related_user': {
                        'id': related_user.pk,
                        'fullname': related_user.first_name + " " + related_user.last_name
                    }
                })

            conversation_messages_unviewed = get_conversation_messages_unviewed(request.user, related_user, mission)
            for message in conversation_messages_unviewed:
                message.is_viewed = True
                message.save()

            if(request.GET.get('refresh')):
                conversation_messages_json = serializers.serialize('json', get_conversation_messages(request.user, related_user, mission))
                return HttpResponse(conversation_messages_json, content_type='application/json')

            self.context['form'] = UserMessageForm()
            self.context['uid'] = uidb64
            self.context['uid_mission'] = urlsafe_base64_encode(force_bytes(mission.pk))
            self.context['related_user'] = related_user
            self.context['conversation_messages'] = get_conversation_messages(request.user, related_user, mission)
            self.context['mission'] = mission
            
            return render(request, self.template_name, self.context)
        else:                
            messages.error(
                request, 
                message=_("Un problème est survenu au moment d'afficher la conversation"),
                extra_tags="alert-danger"
            )
            return redirect('message-inbox')
        
    def post(self, request, uidb64):
        self.context['errors'] = None
        related_user = get_user_by_uid(uidb64)
        mission = get_mission_by_uid(uidb64)

        if related_user is not None:
            self.context['uid'] = uidb64
            self.context['related_user'] = related_user

            form = UserMessageForm(request.POST)

            if (form.is_valid()):
                created_status = UserMessageStatus.objects.get(label="created")

                new_message = UserMessage(
                    sender_user=request.user,
                    receiver_user=related_user,
                    mission=mission,
                    status=created_status,
                    is_support=related_user.is_superuser,
                    content=form.cleaned_data.get('message_content')
                )
                new_message.save()

                if ("mission" in request.headers['Referer']):                
                    messages.success(
                        request, 
                        message=_("Vous avez postulez !"),
                        extra_tags="alert-success"
                    )
                    url = reverse('mission-board')
                    return HttpResponse(url)
                else:
                    new_message_json = serializers.serialize('json', (new_message,))
                    return HttpResponse(new_message_json, content_type='application/json')
            else:
                return JsonResponse(data=form.errors.get_json_data(), safe=False, status=500)
        else:                
            messages.error(
                request, 
                message=_("Destinataire du message inconnu"),
                extra_tags="alert-danger"
            )
            return redirect('message-inbox')
