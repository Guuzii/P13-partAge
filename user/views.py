from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from django.http import HttpResponse
from django.conf import settings

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

from user.models.custom_user import CustomUser

# Create your views here.

def add_to_context(context, **args):
    for arg in args:
        context[arg] = args[arg]
    return context

def handle_uploaded_file(file, filename):
    with open(settings.USER_FILE_UPLOAD_DIR / filename, 'wb+') as destination:
        for chunk in file.chunks(): 
            destination.write(chunk)

    return settings.USER_FILE_UPLOAD_DIR / filename

class Profile(View):
    template_name = 'user/profile.html'
    context = {
        'title': "MON PROFIL",
    }

    def get(self, request):
        if (request.user.is_authenticated):
            self.context['wallet_balance'] = 0 if request.user.wallet is None else request.user.wallet.balance
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
        'form_action': 'register',
        'submit_button_label': 'Inscription',
    }

    def get(self, request):
        self.context['form'] = CustomUserCreationForm()
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = CustomUserCreationForm(request.POST, request.FILES)

        if (form.is_valid()):
            form.save()
            
            user = CustomUser.objects.get(email=form.cleaned_data['email'])
            files = {
                'file_identity': form.cleaned_data['file_identity'],
                'file_criminal': form.cleaned_data['file_criminal']
            }

            for i, (key, file) in enumerate(files.items()):
                extension = file.name.split('.')[-1]
                filename = "file_user_" + str(user.pk) +  "_" + str(i) + "." + extension
                uploaded_filepath = handle_uploaded_file(file, filename)
                if (key == "file_identity"):
                    print("file_identity path : %s"%uploaded_filepath)
                else:
                    print("file_criminal path : %s"%uploaded_filepath)

            return redirect("home")
        else:
            self.context["form"] = form
            self.context["errors"] = form.errors.items()
            return render(request, self.template_name, self.context)

