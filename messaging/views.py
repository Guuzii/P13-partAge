from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _


class MessageInboxView(View):
    template_name = 'messaging/inbox.html'
    context = {
        'title': _("BOITE DE RECEPTION"),
    }

    def get(self, request):
        if (request.user.is_authenticated):
            return render(request, self.template_name, self.context)
        else:
            return redirect('login')
