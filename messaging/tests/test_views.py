import json

from django.core import serializers
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from messaging.forms import UserMessageForm

from messaging.models.message import UserMessage
from messaging.models.message_status import UserMessageStatus

from user.models.custom_user import CustomUser
from user.models.user_type import UserType

from mission.models.mission_category import MissionCategory
from mission.models.mission_status import MissionStatus
from mission.models.mission_bonus_reward import MissionBonusReward
from mission.models.mission import Mission

    
class MessagingInboxTestCase(TestCase):
    def setUp(self):
        self.test_user_type_junior = UserType.objects.create(label="junior")
        self.test_user_type_senior = UserType.objects.create(label="senior")
        self.test_user_1 = CustomUser.objects.create_user(
            first_name="senior",
            last_name="test",
            email="senior@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False,
            user_type=self.test_user_type_senior
        )
        self.test_user_2 = CustomUser.objects.create_user(
            first_name="junior",
            last_name="test",
            email="junior@test.fr",
            birthdate="1910-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False,
            user_type=self.test_user_type_junior
        )
        self.test_mission_status_close = MissionStatus.objects.create(label="close")
        self.test_mission_status_finish = MissionStatus.objects.create(label="finish")
        self.test_mission_status_open = MissionStatus.objects.create(label="open")
        self.test_mission_category = MissionCategory.objects.create(
            label="test_category", 
            base_reward_amount=100, 
            xp_amount=10
        )
        self.test_mission_bonus_reward = MissionBonusReward.objects.create(
            reward_amount=50,
            description="test bonus reward"
        )
        self.test_mission = Mission.objects.create(
            bearer_user=self.test_user_1,
            status=self.test_mission_status_open,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission",
            description="description test mission"
        )
        self.test_message_status_created = UserMessageStatus.objects.create(label='created')

    def test_message_inbox_return_related_user_list(self):
        test_message_1 = UserMessage(
            sender_user=self.test_user_1, 
            receiver_user=self.test_user_2, 
            status=self.test_message_status_created, 
            content="message test 1",
            mission=self.test_mission
        )
        test_response_message_1 = UserMessage(
            sender_user=self.test_user_2, 
            receiver_user=self.test_user_1, 
            status=self.test_message_status_created, 
            content="response message test 1",
            mission=self.test_mission
        )
        test_message_1.save()
        test_response_message_1.save()

        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.get(reverse('message-inbox'))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/inbox.html")

        # Test related users in context
        self.assertTrue(len(response.context['related_users']) > 0)
        uidb64_1 = urlsafe_base64_encode(force_bytes(self.test_user_1.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        uidb64_2 = urlsafe_base64_encode(force_bytes(self.test_user_2.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        for obj in response.context['related_users']:
            self.assertIn(obj['user'], (self.test_user_1, self.test_user_2))
            self.assertIn(obj['uid'], (uidb64_1, uidb64_2))

    def test_message_inbox_return_empty_related_user_list(self):
        self.client.login(username="senior@test.fr", password="test123+")
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
        self.test_user_type_junior = UserType.objects.create(label="junior")
        self.test_user_type_senior = UserType.objects.create(label="senior")
        self.test_user_1 = CustomUser.objects.create_user(
            first_name="senior",
            last_name="test",
            email="senior@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False,
            user_type=self.test_user_type_senior
        )
        self.test_user_2 = CustomUser.objects.create_user(
            first_name="junior",
            last_name="test",
            email="junior@test.fr",
            birthdate="1910-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False,
            user_type=self.test_user_type_junior
        )
        self.test_mission_status_close = MissionStatus.objects.create(label="close")
        self.test_mission_status_finish = MissionStatus.objects.create(label="finish")
        self.test_mission_status_open = MissionStatus.objects.create(label="open")
        self.test_mission_category = MissionCategory.objects.create(
            label="test_category", 
            base_reward_amount=100, 
            xp_amount=10
        )
        self.test_mission_bonus_reward = MissionBonusReward.objects.create(
            reward_amount=50,
            description="test bonus reward"
        )
        self.test_mission = Mission.objects.create(
            bearer_user=self.test_user_1,
            status=self.test_mission_status_open,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission",
            description="description test mission"
        )
        self.test_message_status = UserMessageStatus.objects.create(label='created')
        self.test_message_1 = UserMessage.objects.create(
            sender_user=self.test_user_2, 
            receiver_user=self.test_user_1, 
            status=self.test_message_status, 
            content="message test 1",
            mission=self.test_mission
        )
        self.test_response_message_1 = UserMessage.objects.create(
            sender_user=self.test_user_1, 
            receiver_user=self.test_user_2, 
            status=self.test_message_status, 
            content="response message test 1",
            mission=self.test_mission
        )
        self.test_message_form = UserMessageForm()

    def test_message_conversation_get(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.test_user_2.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.get(reverse('message-conv', args=[uidb64]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test conversation-messages in context
        self.assertTrue(len(response.context['conversation_messages']) > 0)
        for message in response.context['conversation_messages']:
            self.assertIn(message.pk, (self.test_message_1.pk, self.test_response_message_1.pk))

        # Test context content
        self.assertEqual(response.context['uid'], uidb64)
        self.assertEqual(response.context['related_user'], self.test_user_2)
        self.assertEqual(response.context['uid_mission'], urlsafe_base64_encode(force_bytes(self.test_mission.pk)))
        self.assertEqual(response.context['form_id'], "send-message-form")
        self.assertEqual(response.context['form_action'], "message-conv")
        self.assertEqual(response.context['submit_button_label'], "Envoyer")
        self.assertEqual(response.context['back_url_name'], "message-inbox")       
        
        # Test form used is the right one
        self.assertEqual(
            response.context["form"].fields.keys(), self.test_message_form.fields.keys()
        )
        
    def test_message_conversation_get_refresh(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.test_user_2.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        self.client.login(username="senior@test.fr", password="test123+")
        url = reverse('message-conv', args=[uidb64]) + '?refresh=1'
        response = self.client.get(url)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test Json response content
        messages_json = serializers.serialize('json', UserMessage.objects.all().order_by('pk'))
        self.assertJSONEqual(response.content.decode('utf8'), messages_json)
        
    def test_message_conversation_get_infos(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.test_user_2.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        self.client.login(username="senior@test.fr", password="test123+")
        url = reverse('message-conv', args=[uidb64]) + '?infos=1'
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
        uidb64 = urlsafe_base64_encode(force_bytes(-1)) + "-" + urlsafe_base64_encode(force_bytes(-1))
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.get(reverse('message-conv', args=[uidb64]))

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
        uidb64 = urlsafe_base64_encode(force_bytes(self.test_user_2.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        post_args = {
            'message_content': "new message test",
        }
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('message-conv', args=[uidb64,]), post_args, HTTP_REFERER="messaging")

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

    def test_message_conversation_post_apply(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.test_user_1.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        post_args = {
            'message_content': "new message test apply",
        }
        self.client.login(username="junior@test.fr", password="test123+")
        response = self.client.post(reverse('message-conv', args=[uidb64,]), post_args, HTTP_REFERER="mission")

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="messaging/conversation.html")

        # Test new message created
        last_message = UserMessage.objects.last()
        self.assertEqual(post_args['message_content'], last_message.content)
        self.assertEqual(self.test_user_2, last_message.sender_user)
        self.assertEqual(self.test_user_1, last_message.receiver_user)

        # Test Json response content
        self.assertEqual(reverse('mission-board'), response.content.decode('utf8'))

    def test_message_conversation_post_form_invalid(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.test_user_2.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        post_args = {
            'message_content': "",
        }
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('message-conv', args=[uidb64,]), post_args, HTTP_REFERER="messaging")

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
        uidb64 = urlsafe_base64_encode(force_bytes(-1)) + "-" + urlsafe_base64_encode(force_bytes(-1))
        post_args = {
            'message_content': "test message wrong uid",
        }
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('message-conv', args=[uidb64,]), post_args, HTTP_REFERER="messaging")

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
