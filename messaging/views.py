from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from messaging.forms import UserMessageForm

from messaging.models.message import UserMessage
from messaging.models.message_status import UserMessageStatus

from user.models.custom_user import CustomUser


def get_user_by_uid(uidb64):    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    return user

def get_conversation_messages(auth_user, related_user):
    conversation_messages = UserMessage.objects.filter(
        Q(Q(sender_user=auth_user) & Q(receiver_user=related_user)) |
        Q(Q(sender_user=related_user) & Q(receiver_user=auth_user))
    ).order_by('created_at')

    return conversation_messages


class MessageInbox(View):
    template_name = 'messaging/inbox.html'
    context = {
        'title': _("BOITE DE RECEPTION"),
    }

    def get(self, request):
        sender_user_messages_distinct = UserMessage.objects.filter(sender_user=request.user).order_by('receiver_user').distinct('receiver_user')
        receiver_user_messages_distinct = UserMessage.objects.filter(receiver_user=request.user).order_by('sender_user').distinct('sender_user')
        related_users = []

        for message in sender_user_messages_distinct:
            related_users.append(message.receiver_user)
        
        for message in receiver_user_messages_distinct:
            if (message.sender_user not in related_users):
                related_users.append(message.sender_user)

        related_users_with_uid = []

        for user in related_users:
            related_users_with_uid.append({
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk))
            })
        
        self.context['related_users'] = related_users_with_uid
        return render(request, self.template_name, self.context)


class MessageConversation(View):
    template_name = 'messaging/conversation.html'
    context = {
        'title': _("CONVERSATION"),
        'form_action': 'message-conv',
        'submit_button_label': _("Envoyer"),
    }

    def get(self, request, uidb64):
        self.context['errors'] = None
        related_user = get_user_by_uid(uidb64)

        if related_user is not None:            
            self.context['form'] = UserMessageForm()
            self.context['uid'] = uidb64
            self.context['related_user'] = related_user
            self.context['conversation_messages'] = get_conversation_messages(request.user, related_user)
            
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

        if related_user is not None:
            self.context['uid'] = uidb64
            self.context['related_user'] = related_user

            form = UserMessageForm(request.POST)

            if (form.is_valid()):
                sended_status = UserMessageStatus.objects.get(label="sended")

                new_message = UserMessage(
                    sender_user=request.user,
                    receiver_user=related_user,
                    status=sended_status,
                    is_support=related_user.is_superuser,
                    content=form.cleaned_data.get('message_content')
                )
                new_message.save()

                return redirect('message-conv', uidb64=uidb64)
            else:
                self.context['conversation_messages'] = get_conversation_messages(request.user, related_user)
                self.context['form'] = form
                self.context['errors'] = form.errors.items()

                return render(request, self.template_name, self.context)
        else:                
            messages.error(
                request, 
                message=_("Destinataire du message inconnu"),
                extra_tags="alert-danger"
            )
            return redirect('message-conv', uidb64=uidb64)
