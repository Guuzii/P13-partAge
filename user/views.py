from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
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
    CustomUserPwdForgotForm,
    CustomUserPwdResetForm
)

from user.models.custom_user import CustomUser
from user.models.document import Document
from user.models.document_type import DocumentType

from user.tokens import account_activation_token, password_reset_token

from mission.models.mission import Mission
from mission.models.mission_status import MissionStatus


def handle_uploaded_file(file, filename):
    with open(settings.USER_FILE_UPLOAD_DIR / filename, 'wb+') as destination:
        for chunk in file.chunks(): 
            destination.write(chunk)

    return filename

def custom_send_email(request, user, subject, template, pwd=False):
    site = get_current_site(request)
    token = password_reset_token.make_token(user) if pwd else account_activation_token.make_token(user)
    protocol = "https" if request.is_secure else "http"
    if  site.domain in ("127.0.0.1", "localhost", "174.138.15.127",):
        protocol = "http"

    content = render_to_string(template, {
        'user': user,
        'protocol': "protocol",
        'domain': site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token
    })

    sended_message = send_mail(
        subject=subject,
        message=content,
        from_email="contact@partage.fr",
        recipient_list=[
            user.email,
        ],
    )

    if sended_message > 0:
        return True
    else :
        if pwd:
            message_content = _("Une erreur s'est produite au moment d'envoyer l'email de réinitialisation de mot de passe.")
        else:
            message_content = _("Une erreur s'est produite au moment d'envoyer l'email de vérification de compte.")

        messages.error(
            request, 
            message=message_content,
            extra_tags="alert-danger"
        )
        return False

def get_user_by_uid(uidb64):    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    return user


class UserProfile(View):
    template_name = 'user/profile.html'
    context = {
        'title': _("MON PROFIL"),
    }

    def get(self, request):
        if (request.GET.get('statsnum')):
            mission_status_finish = MissionStatus.objects.get(label="finish")
            stats_json = {
                'user_count': CustomUser.objects.exclude(is_superuser=True).count(),
                'mission_count': Mission.objects.all().count(),
                'mission_end_count': Mission.objects.filter(status=mission_status_finish).count()
            }
            return JsonResponse(stats_json, safe=False)

        if (request.user.is_authenticated):
            self.context['wallet_balance'] = 0 if request.user.wallet is None else request.user.wallet.balance
            return render(request, self.template_name, self.context)
        else:
            return redirect('login')


class UserRegister(View):
    template_name = 'user/register.html'
    email_template = 'user/emails/email_validation.html'
    email_subject = _("Verification de votre adresse email")
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
            
            user = CustomUser.objects.get(email=form.cleaned_data.get('email'))
            files = {
                'file_identity': form.cleaned_data.get('file_identity'),
                'file_criminal': form.cleaned_data.get('file_criminal')
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

            email_sended = custom_send_email(request, user, self.email_subject, self.email_template)

            if email_sended:
                messages.success(
                    request, 
                    message=_("Un email vous a été envoyé. Merci de cliquer sur le lien contenu dans celui-ci afin de valider votre adresse email."),
                    extra_tags="alert-success"
                )

            return redirect('home')
        else:
            self.context['form'] = form
            self.context['errors'] = form.errors.items()
            return render(request, self.template_name, self.context)


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


class UserVerifyEmail(View):
    template_name = 'user/email_verify.html'
    context = {
        'title': _("VALIDATION ADRESSE EMAIL"),
    }

    def get(self, request, uidb64, token):
        user = get_user_by_uid(uidb64)

        if user is not None and account_activation_token.check_token(user, token):
            user.email_validated = True
            user.save()
            self.context['verification_message'] = _("Votre adresse email a été validée avec succés")
            return render(request, self.template_name, self.context)
        else:
            self.context['verification_message'] = _("Le lien de confirmation de votre adresse mail n'est plus valide.")
            return render(request, self.template_name, self.context)


class UserForgotPwd(View):
    template_name = 'user/password_forgot.html'
    email_template = 'user/emails/reset_password.html'
    email_subject = _("Réinitialisation de mot de passe")
    context = {
        'title': _("REINITIALISATION MOT DE PASSE"),
        'form_action': 'pwd-forgot',
        'submit_button_label': _("Envoyer"),
    }

    def get(self, request):
        if (request.user.is_authenticated):
            user = CustomUser.objects.get(pk=request.user.pk)
            user.is_active = False
            user.reset_password = True                
            user.save()

            email_sended = custom_send_email(request, user, self.email_subject, self.email_template,pwd=True)

            if email_sended:                
                messages.success(
                    request, 
                    message=_("Un email vous a été envoyé. Merci de cliquer sur le lien contenu dans celui-ci afin de modifier votre mot de passe."),
                    extra_tags="alert-success"
                )
            else:
                 messages.error(
                    request, 
                    message=_("Erreur lors de l'envoi de l'email. Merci de refaire une demande de changement de mot de passe."),
                    extra_tags="alert-danger"
                )
            
            logout(request)
            return redirect('home')
        else:
            self.context['form'] = CustomUserPwdForgotForm()
            return render(request, self.template_name, self.context)

    def post(self, request):
        form = CustomUserPwdForgotForm(request.POST)
        
        if (form.is_valid()):
            email = form.cleaned_data.get('email')
            queryset = CustomUser.objects.filter(email=email)

            if (len(queryset) > 0):
                user = queryset[0]

                # if email associated user is_active or already have asked for a pwd reset
                if (user.is_active or user.reset_password): 
                    user.is_active = False
                    user.reset_password = True

                    email_sended = custom_send_email(request, user, self.email_subject, self.email_template,pwd=True)             
                    
                    if (email_sended):
                        user.save()                

            messages.success(
                request, 
                message=_("Si cette adresse email existe, un email sera envoyé sur ce compte"),
                extra_tags="alert-success"
            )

            return redirect('home')
        else:
            self.context['form'] = form
            self.context['errors'] = form.errors.items()
            return render(request, self.template_name, self.context)


class UserResetPwd(View):    
    template_name = 'user/password_reset.html'
    context = {
        'title': _("REINITIALISATION MOT DE PASSE"),
        'form_action': 'pwd-reset',
        'submit_button_label': _("Valider"),
    }

    def get(self, request, uidb64, token):
        user = get_user_by_uid(uidb64)

        if user is not None and password_reset_token.check_token(user, token):
            self.context['form'] = CustomUserPwdResetForm(user)
            self.context['uid'] = uidb64
            self.context['token'] = token
            return render(request, self.template_name, self.context)
        else:
            self.context['reset_message'] = _("Le Lien de changement de mot de passe n'est plus valide")
            return render(request, self.template_name, self.context)

    def post(self, request, uidb64, token):
        user = get_user_by_uid(uidb64)

        if user is not None and password_reset_token.check_token(user, token):
            form = CustomUserPwdResetForm(user, data=request.POST)

            if (form.is_valid()):
                form.save()
                update_session_auth_hash(request, form.user)
                
                user.is_active = True
                user.reset_password = False
                user.save()
                
                messages.success(
                    request, 
                    message=_("Votre mot de passe à bien été modifié."),
                    extra_tags="alert-success"
                )

                return redirect('home')
            else:
                self.context['form'] = form
                self.context['errors'] = form.errors.items()
                self.context['uid'] = uidb64
                self.context['token'] = token
                return render(request, self.template_name, self.context)
