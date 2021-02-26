import os

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages, get_level
from django.conf import settings

from unittest.mock import Mock, patch

from os.path import isfile

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

# Create your tests here.

# Homepage page
class HomePageTestCase(TestCase):
    def test_homepage(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class UserRegisterView(TestCase):
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].fields.keys(), self.test_register_form.fields.keys()
        )

    def test_user_register_post_valid_form(self):

        response = self.client.post(reverse('register'), self.post_args)

        # Test last created user and his documents
        last_user_created = CustomUser.objects.latest('id')
        user_documents = Document.objects.filter(user=last_user_created)
        self.assertEqual(last_user_created.email, "test@test.fr")
        self.assertEqual(len(user_documents), 2)
        
        # Test that there is only one message and message content
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            "Un email vous a été envoyé. Merci de cliquer sur le lien contenu dans celui-ci afin de valider votre adresse email."
        )

        # Test if uploaded identity file exists
        file_identity_name = "file_user_" + str(last_user_created.pk) +  "_" + str(0) + ".png"
        file_identity_path = settings.USER_FILE_UPLOAD_DIR / file_identity_name
        self.assertTrue(os.path.isfile(file_identity_path))
        os.remove(file_identity_path)
        
        # Test if uploaded criminal file exists
        file_criminal_name = "file_user_" + str(last_user_created.pk) +  "_" + str(1) + ".png"
        file_criminal_path = settings.USER_FILE_UPLOAD_DIR / file_criminal_name
        self.assertTrue(os.path.isfile(file_criminal_path))
        os.remove(file_criminal_path)
        
        # Test redirection
        self.assertRedirects(response=response, expected_url=reverse('home'))

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



class UserLoginView(TestCase):
    pass


class UserProfileView(TestCase):
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user.pk, int(self.client.session["_auth_user_id"])) # test user is authenticated
        self.assertTemplateUsed(template_name="user/profile.html")

    def test_user_profile_redirect_login(self):
        response = self.client.get(reverse('user-profile'))
        self.assertRedirects(response=response, expected_url=reverse('login'))
        self.assertTemplateUsed(template_name="user/login.html")
