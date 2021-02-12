from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    LoginView, 
    LogoutView
)
from django.contrib.auth.decorators import login_required

from user.forms import (
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserChangeForm,
)

# Create your views here.

def add_to_context(context, **args):
    for arg in args:
        context[arg] = args[arg]
    return context


class Profile(View):
    template_name = 'user/profile.html'
    context = {
        'title': "MON PROFIL",
    }

    def get(self, request):
        if (request.user.is_authenticated):
            self.context['wallet_balance'] = 0 if request.user.id_wallet is None else request.user.id_wallet.balance
            return render(request, self.template_name, self.context)
        else:
            return redirect('login')


class UserLogin(LoginView):    
    template_name = 'user/login.html'
    authentication_form = CustomUserLoginForm
    extra_context = {
        'title': "CONNEXION",
        'form_action': 'login',
        'submit_button_label': 'Connexion',
    }


class UserLogout(LogoutView):    
    def get(self, request):
        """Logout authenticated user and redirect to Homepage"""
        return redirect("home")


class UserRegister(View):
    template_name = 'user/register.html'
    context = {
        'title': 'INSCRIPTION',
        'form': CustomUserCreationForm,
        'form_action': 'register',
        'submit_button_label': 'Inscription',
    }

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if (form.is_valid):
            print('FORM VALID : ', form)
            form.save()
            username = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")
        else:
            self.context["form"] = form
            self.context["errors"] = form.errors.items()
            return render(request, self.template_name, self.context)

