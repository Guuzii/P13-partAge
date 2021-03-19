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

from user.models.user_type import UserType

class MissionBoard(View):
    template_name = 'mission/board.html'
    context = {
        'title': _("TABLEAU DES MISSIONS"),
    }

    def get(self, request):        
        return render(request, self.template_name, self.context)


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

        if(request.user.user_type.pk == senior_type.pk):
            self.context['form'] = CreateMissionForm()
            return render(request, self.template_name, self.context)
        else:
            return redirect('mission-board')
