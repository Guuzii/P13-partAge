from os.path import isfile as os_isfile
from os import remove as os_removefile

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.contrib.messages import get_messages, get_level
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from unittest.mock import Mock, patch

from user.models.custom_user import CustomUser
from user.models.document_type import DocumentType
from user.models.document import Document

from user.forms import (
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserChangeForm,
    CustomUserPwdForgotForm,
    CustomUserPwdResetForm
)

from user.tokens import account_activation_token, password_reset_token

# Create your tests here.

class HomePageTestCase(TestCase):
    def test_homepage_get(self):
        response = self.client.get(reverse('home'))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="platform/home.html")


class UserRegisterTestCase(TestCase):
    def setUp(self):
        self.test_register_form = CustomUserCreationForm()
        for document_type in settings.DOCUMENT_TYPES:
            DocumentType.objects.create(label=document_type)
        
        file_identity = SimpleUploadedFile(name='test_identity.png', content=b"file_content_identity", content_type="image/png")
        file_criminal = SimpleUploadedFile(name='test_criminal.png', content=b"file_content_criminal", content_type="image/png")
        self.post_args = {
            'first_name': "testeur",
            'last_name': "test",
            'email': "test@test.fr",
            'birthdate': "01-01-1900",
            'password1': "test123+",
            'password2': "test123+",
            'file_identity': file_identity,
            'file_criminal': file_criminal
        }

    def test_user_register_get(self):
        response = self.client.get(reverse("register"))

        # Test form used
        self.assertEqual(
            response.context["form"].fields.keys(), self.test_register_form.fields.keys()
        )

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="user/register.html")

    def test_user_register_post_valid_form(self):
        response = self.client.post(reverse('register'), self.post_args)

        # Test last created user and related documents
        last_user_created = CustomUser.objects.latest('id')
        user_documents = Document.objects.filter(user=last_user_created)
        self.assertEqual(last_user_created.email, "test@test.fr")
        self.assertEqual(len(user_documents), 2)

        # Test email sended
        sended_email = len(mail.outbox)
        self.assertEqual(sended_email, 1)
        
        # Test messages not empty and messages content
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            "Un email vous a été envoyé. Merci de cliquer sur le lien contenu dans celui-ci afin de valider votre adresse email."
        )

        # Test if uploaded identity file exists
        file_identity_name = "file_user_" + str(last_user_created.pk) +  "_" + str(0) + ".png"
        file_identity_path = settings.USER_FILE_UPLOAD_DIR / file_identity_name
        self.assertTrue(os_isfile(file_identity_path))
        os_removefile(file_identity_path)
        
        # Test if uploaded criminal file exists
        file_criminal_name = "file_user_" + str(last_user_created.pk) +  "_" + str(1) + ".png"
        file_criminal_path = settings.USER_FILE_UPLOAD_DIR / file_criminal_name
        self.assertTrue(os_isfile(file_criminal_path))
        os_removefile(file_criminal_path)
        
        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('home'))
        self.assertTemplateUsed(template_name="platform/home.html")

    def test_user_register_post_invalid_infos(self):
        self.post_args['first_name'] = ""
        self.post_args['last_name'] = ""
        self.post_args['email'] = "badEmailAddress@@test.fr.dev"
        self.post_args['birthdate'] = "123-18-12369"
        self.post_args['password1'] = "test123+"
        self.post_args['password2'] = "test123456+"

        response = self.client.post(reverse('register'), self.post_args)

        # Test errors not empty and errors content
        self.assertTrue(len(response.context['errors']) > 0)
        for error in response.context['errors']:
            self.assertIn(error[0], ('first_name', 'last_name', 'email', 'birthdate', 'password1', 'password2'))

    def test_user_register_post_invalid_files(self):
        file_identity = SimpleUploadedFile(name='test_identity.png', content=b"file_content_identity", content_type="image/test")
        file_criminal = SimpleUploadedFile(name='test_criminal.png', content=b"", content_type="image/png")
        self.post_args['file_identity'] = file_identity
        self.post_args['file_criminal'] = file_criminal        

        response = self.client.post(reverse('register'), self.post_args)

        # Test errors not empty and errors content
        self.assertTrue(len(response.context['errors']) > 0)
        for error in response.context['errors']:
            self.assertIn(error[0], ('file_identity', 'file_criminal'))


class UserLoginTestCase(TestCase):
    def setUp(self):
        self.test_user_active = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_user_inactive = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="testinactive@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=False,
            is_superuser=False
        )
        self.test_login_form = CustomUserLoginForm()

    def test_user_login_get(self):
        response = self.client.get(reverse("login"))
        
        # Test form used is the right one
        self.assertEqual(
            response.context["form"].fields.keys(), self.test_login_form.fields.keys()
        )

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="user/login.html")

    def test_user_login_post_valid_form(self):
        post_args = {
            'username': "test@test.fr",
            'password': "test123+"
        }

        response = self.client.post(reverse('login'), post_args)
        
        # Test user is authenticated
        self.assertIsNotNone(self.client.session.get("_auth_user_id"))
        self.assertEqual(self.test_user_active.pk, int(self.client.session.get("_auth_user_id"))) 

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('home'))
        self.assertTemplateUsed(template_name="platform/home.html")

    def test_user_login_post_invalid_credentials(self):
        post_args = {
            'username': "baduser@baduser.fr",
            'password': "test123+"
        }

        response = self.client.post(reverse('login'), post_args)

        # Test user is not authenticated
        self.assertIsNone(self.client.session.get("_auth_user_id"))

        # Test errors not empty
        self.assertTrue(len(response.context['form'].errors) > 0)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="user/login.html")
        
    def test_user_login_post_inactive_user(self):
        post_args = {
            'username': "testinactive@test.fr",
            'password': "test123+"
        }

        response = self.client.post(reverse('login'), post_args)

        # Test user is not authenticated
        self.assertIsNone(self.client.session.get("_auth_user_id"))

        # Test errors not empty and errors content
        self.assertTrue(len(response.context['form'].errors) > 0)
        for error in response.context['form'].errors:
            self.assertIn(error, ('username',))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="user/login.html")


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.test_user = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )

    def test_user_profile_return_profile(self):
        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.get(reverse('user-profile'))  

        # Test user is authenticated
        self.assertIsNotNone(self.client.session.get("_auth_user_id"))
        self.assertEqual(self.test_user.pk, int(self.client.session.get("_auth_user_id")))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="user/profile.html")

    def test_user_profile_redirect_login(self):
        response = self.client.get(reverse('user-profile'))

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('login'))
        self.assertTemplateUsed(template_name="user/login.html")


class UserLogoutTestCase(TestCase):
    def setUp(self):
        self.test_user = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.client.login(username="test@test.fr", password="test123+")

    def test_user_logout_get(self):
        # Test user is authenticated
        self.assertIsNotNone(self.client.session.get("_auth_user_id"))
        self.assertEqual(self.test_user.pk, int(self.client.session.get("_auth_user_id"))) 
        
        response = self.client.get(reverse("logout"))

        # Test user is not authenticated
        self.assertIsNone(self.client.session.get("_auth_user_id")) 

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('home'))
        self.assertTemplateUsed(template_name="platform/home.html")


class UserVerifyEmailTestCase(TestCase):
    def setUp(self):
        self.test_user = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=False,
            is_active=False,
            is_superuser=False
        )
        self.token = account_activation_token.make_token(self.test_user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.test_user.pk))

    def test_user_verify_email_valid_link(self):
        response = self.client.get(reverse('verify-email', args=[self.uidb64, self.token]))

        verified_user = CustomUser.objects.get(pk=self.test_user.pk)

        # Test user email validated
        self.assertTrue(verified_user.email_validated)

        # Test email verification message
        self.assertIsNotNone(response.context['verification_message'])
        self.assertEqual(
            response.context['verification_message'],
            "Votre adresse email a été validée avec succés"
        )

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="user/email_verify.html")

    def test_user_verify_email_invalid_link(self):
        self.uidb64 = urlsafe_base64_encode(force_bytes(-1))
        response = self.client.get(reverse('verify-email', args=[self.uidb64, self.token]))

        verified_user = CustomUser.objects.get(pk=self.test_user.pk)

        # Test user email not validated
        self.assertFalse(verified_user.email_validated)

        # Test email verification message
        self.assertIsNotNone(response.context['verification_message'])
        self.assertEqual(
            response.context['verification_message'],
            "Le lien de confirmation de votre adresse mail n'est plus valide."
        )

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="user/email_verify.html")
