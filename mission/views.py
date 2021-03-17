from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q


class MissionBoard(View):
    template_name = 'messaging/inbox.html'
    context = {
        'title': _("MISSIONS DISPONIBLE"),
    }

    def get(self, request):        
        return render(request, self.template_name, self.context)    
