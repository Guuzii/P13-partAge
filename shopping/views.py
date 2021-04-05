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

from user.models.user_type import UserType
from user.models.custom_user import CustomUser


class ShoppingProducts(View):
    template_name = 'shop/products.html'
    context = {
        'title': _("TITRE SHOPPING PRODUITS"),
    }    

    def get(self, request):
        senior_type = UserType.objects.get(label__iexact="senior")

        if (request.user.user_type == senior_type):
            messages.error(
                request, 
                message=_("Vous devez être un utilisateur de type Junior pour accéder à la boutique"),
                extra_tags="alert-danger"
            )
            return redirect('home')

        return render(request, self.template_name, self.context)
