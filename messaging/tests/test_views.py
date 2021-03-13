import json

from os.path import isfile as os_isfile
from os import remove as os_removefile

from django.core import serializers
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.contrib.messages import get_messages
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from messaging.forms import UserMessageForm

from messaging.models.message import UserMessage
from messaging.models.message_status import UserMessageStatus

from user.models.custom_user import CustomUser


class MessagingInboxTestCase(TestCase):
    def setUp(self):
        self.test_user_1 = CustomUser.objects.create_user(
            first_name="test",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_user_2 = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="testeur@test.fr",
            birthdate="1910-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_message_status = UserMessageStatus(label='test_message_status')
        self.test_message_status.save()

    def test_message_inbox_return_related_user_list(self):
        test_message_1 = UserMessage(
            sender_user=self.test_user_1, 
            receiver_user=self.test_user_2, 
            status=self.test_message_status, 
            content="message test 1"
        )
        test_response_message_1 = UserMessage(
            sender_user=self.test_user_2, 
            receiver_user=self.test_user_1, 
            status=self.test_message_status, 
            content="response message test 1"
        )
        test_message_1.save()
        test_response_message_1.save()

        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.get(reverse('message-inbox'))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/inbox.html")

        # Test related users in context
        self.assertTrue(len(response.context['related_users']) > 0)
        for obj in response.context['related_users']:
            self.assertIn(obj['user'], (self.test_user_1, self.test_user_2))
            self.assertIn(obj['uid'], (urlsafe_base64_encode(force_bytes(self.test_user_1.pk)), urlsafe_base64_encode(force_bytes(self.test_user_2.pk))))

    def test_message_inbox_return_empty_related_user_list(self):
        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.get(reverse('message-inbox'))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/inbox.html")

        # Test related users in context
        self.assertFalse(len(response.context['related_users']) > 0)
    
    def test_message_inbox_redirect_login(self):
        response = self.client.get(reverse('message-inbox'))

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url='/user/login/?next=%2Fmessage%2F')
        self.assertTemplateUsed(template_name="user/login.html")


class MessagingConversationTestCase(TestCase):
    def setUp(self):
        self.test_user_1 = CustomUser.objects.create_user(
            first_name="test",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_user_2 = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="testeur@test.fr",
            birthdate="1910-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_message_status = UserMessageStatus(label='created')
        self.test_message_status.save()
        self.test_message_1 = UserMessage(
            sender_user=self.test_user_1, 
            receiver_user=self.test_user_2, 
            status=self.test_message_status, 
            content="message test 1"
        )
        self.test_response_message_1 = UserMessage(
            sender_user=self.test_user_2, 
            receiver_user=self.test_user_1, 
            status=self.test_message_status, 
            content="response message test 1"
        )
        self.test_message_1.save()
        self.test_response_message_1.save()
        self.test_message_form = UserMessageForm()

    def test_message_conversation_get(self):
        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.get(reverse('message-conv', args=[urlsafe_base64_encode(force_bytes(self.test_user_2.pk))]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test conversation-messages in context
        self.assertTrue(len(response.context['conversation_messages']) > 0)
        for message in response.context['conversation_messages']:
            self.assertIn(message.pk, (self.test_message_1.pk, self.test_response_message_1.pk))

        # Test context content
        self.assertEqual(response.context['uid'], urlsafe_base64_encode(force_bytes(self.test_user_2.pk)))
        self.assertEqual(response.context['related_user'], self.test_user_2)       
        
        # Test form used is the right one
        self.assertEqual(
            response.context["form"].fields.keys(), self.test_message_form.fields.keys()
        )    
        
    def test_message_conversation_get_refresh(self):
        self.client.login(username="test@test.fr", password="test123+")
        url = reverse('message-conv', args=[urlsafe_base64_encode(force_bytes(self.test_user_2.pk))]) + '?refresh=1'
        response = self.client.get(url)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test Json response content
        messages_json = serializers.serialize('json', UserMessage.objects.all())
        self.assertJSONEqual(response.content.decode('utf8'), messages_json)
        
    def test_message_conversation_get_infos(self):
        self.client.login(username="test@test.fr", password="test123+")
        url = reverse('message-conv', args=[urlsafe_base64_encode(force_bytes(self.test_user_2.pk))]) + '?infos=1'
        response = self.client.get(url)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test Json response content
        infos = {
            'status_created_id': self.test_message_status.pk,
            'user': {
                'id': self.test_user_1.pk,
                'fullname': self.test_user_1.first_name + " " + self.test_user_1.last_name
            },
            'related_user': {
                'id': self.test_user_2.pk,
                'fullname': self.test_user_2.first_name + " " + self.test_user_2.last_name
            }
        }
        self.assertJSONEqual(response.content.decode('utf8'), infos)

    def test_message_conversation_get_error(self):
        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.get(reverse('message-conv', args=[urlsafe_base64_encode(force_bytes(-1))]))

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('message-inbox'))
        self.assertTemplateUsed(template_name="messaging/inbox.html")
        
        # Test messages not empty and messages content
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            "Un problème est survenu au moment d'afficher la conversation"
        )

    def test_message_conversation_post(self):
        post_args = {
            'message_content': "new message test",
        }
        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.post(reverse('message-conv', args=[urlsafe_base64_encode(force_bytes(self.test_user_2.pk))]), post_args)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test new message created
        last_message = UserMessage.objects.last()
        self.assertEqual(post_args['message_content'], last_message.content)
        self.assertEqual(self.test_user_1, last_message.sender_user)
        self.assertEqual(self.test_user_2, last_message.receiver_user)

        # Test Json response content
        new_message_json = serializers.serialize('json', (last_message, ))
        self.assertJSONEqual(new_message_json, response.content.decode('utf8'))

    def test_message_conversation_post_form_invalid(self):
        post_args = {
            'message_content': "",
        }
        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.post(reverse('message-conv', args=[urlsafe_base64_encode(force_bytes(self.test_user_2.pk))]), post_args)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test Json response content
        errors = {
            'message_content': [
                {
                    'message': "Vous ne pouvez pas envoyer un message vide",
                    'code': "required"
                },
            ],
        }
        errors_json = json.dumps(errors)
        self.assertJSONEqual(errors_json, response.content.decode('utf8'))

    def test_message_conversation_post_uid_invalid(self):
        post_args = {
            'message_content': "test message wrong uid",
        }
        self.client.login(username="test@test.fr", password="test123+")
        response = self.client.post(reverse('message-conv', args=[urlsafe_base64_encode(force_bytes(-1))]), post_args)

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('message-inbox'))
        self.assertTemplateUsed(template_name="messaging/inbox.html")
        
        # Test messages not empty and messages content
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            "Destinataire du message inconnu"
        )
