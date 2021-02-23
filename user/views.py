from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    LoginView, 
    LogoutView
)
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from user.forms import (
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserChangeForm,
)
from user.models.custom_user import CustomUser
from user.models.document import Document
from user.models.document_type import DocumentType
from user.tokens import account_activation_token, password_reset_token

# Create your views here.

def add_to_context(context, **args):
    for arg in args:
        context[arg] = args[arg]
    return context

def handle_uploaded_file(file, filename):
    with open(settings.USER_FILE_UPLOAD_DIR / filename, 'wb+') as destination:
        for chunk in file.chunks(): 
            destination.write(chunk)

    return filename

class UserProfile(View):
    template_name = 'user/profile.html'
    context = {
        'title': _("MON PROFIL"),
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
        'title': _("CONNEXION"),
        'form_action': 'login',
        'submit_button_label': _("Connexion"),
    }


class UserLogout(LogoutView):    
    def get(self, request):
        """Logout authenticated user and redirect to Homepage"""
        return redirect("home")


class UserRegister(View):
    template_name = 'user/register.html'
    email_template = 'user/emails/email_validation.html'
    context = {
        'title': _("INSCRIPTION"),
        'form_action': 'register',
        'submit_button_label': _("Inscription"),
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
                uploaded_filename = handle_uploaded_file(file, filename)

                if (key == "file_identity"):
                    document_type = DocumentType.objects.get(label=settings.DOCUMENT_TYPES[0])
                else:
                    document_type = DocumentType.objects.get(label=settings.DOCUMENT_TYPES[1])

                document = Document(path=settings.USER_STATIC_UPLOAD_DIR + uploaded_filename, user=user, document_type=document_type)
                document.save()

            site = get_current_site(request)
            email_subject = _("Verification de votre adresse email")
            email_content = render_to_string(self.email_template, {
                'user': user,
                'protocol': 'http',
                'domain': site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            
            send_mail(
                subject=email_subject,
                message=email_content,
                from_email="test@test.fr",
                recipient_list=[
                    user.email,
                ],
            )

            messages.success(request, _("Merci de confirmer votre email pour valider votre demande d'inscription"))

            return redirect("home")
        else:
            self.context["form"] = form
            self.context["errors"] = form.errors.items()
            return render(request, self.template_name, self.context)


class UserVerifyEmail(View):
    template_name = 'user/email_verify.html'
    context = {
        'title': _("VALIDATION ADRESSE EMAIL"),
    }

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.email_validated = True
            user.save()
            self.context['verification_message'] = _('Votre adresse email a été validée avec succés')
            return render(request, self.template_name, self.context)
        else:
            self.context['verification_message'] = _("Le lien de confirmation de votre adresse mail n'est plus valide")
            return render(request, self.template_name, self.context)


class UserForgotPwd(View):
    template_name = 'user/email_verify.html'
    context = {
        'title': _("VALIDATION ADRESSE EMAIL"),
    }

    def get(self, request):
        pass
