import json

from django.core import serializers
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Q

from mission.models.mission_category import MissionCategory
from mission.models.mission_status import MissionStatus
from mission.models.mission_bonus_reward import MissionBonusReward
from mission.models.mission import Mission
from mission.forms import CreateMissionForm

from user.models.user_type import UserType
from user.models.custom_user import CustomUser
from user.models.wallet import Wallet

from messaging.models.message_status import UserMessageStatus
from messaging.forms import UserMessageForm


class MissionBoardTestCase(TestCase):
    def setUp(self):
        self.test_user_type_junior = UserType.objects.create(label="junior")
        self.test_user_type_senior = UserType.objects.create(label="senior")
        self.test_user_senior = CustomUser.objects.create_user(
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
        self.test_user_junior = CustomUser.objects.create_user(
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
        self.test_mission_status_open = MissionStatus.objects.create(label="open")
        self.test_mission_status_ongoing = MissionStatus.objects.create(label="ongoing")
        self.test_mission_status_finish = MissionStatus.objects.create(label="finish")
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
            bearer_user=self.test_user_senior,
            status=self.test_mission_status_open,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission",
            description="description test mission"
        )
        self.test_mission2 = Mission.objects.create(
            bearer_user=self.test_user_senior,
            status=self.test_mission_status_close,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission2",
            description="description test mission2"
        )

    def test_mission_board_default_get(self):
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.get(reverse('mission-board'))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/board.html")

        # Test related users in context
        self.assertTrue(len(response.context['missions']) > 0)
        uidb64 = urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        for obj in response.context['missions']:
            self.assertIn(obj['mission'], (self.test_mission,))
            self.assertIn(obj['uid'], (uidb64,))

    def test_mission_board_specific_status_get(self):
        self.client.login(username="senior@test.fr", password="test123+")
        url = reverse('mission-board') + '?status=close'
        response = self.client.get(url)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/board.html")

        # Test Json response content
        missions_json = [{
            'mission': serializers.serialize('json', (self.test_mission2,)),
            'uid': urlsafe_base64_encode(force_bytes(self.test_mission2.pk))
        }]
        self.assertJSONEqual(response.content.decode('utf8'), missions_json)


class MissionDetailsTestCase(TestCase):
    def setUp(self):
        self.test_message_status_created = UserMessageStatus.objects.create(label="created")
        self.test_user_type_junior = UserType.objects.create(label="junior")
        self.test_user_type_senior = UserType.objects.create(label="senior")
        self.test_user_senior = CustomUser.objects.create_user(
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
        self.test_user_junior = CustomUser.objects.create_user(
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
        self.test_mission_status_open = MissionStatus.objects.create(label="open")
        self.test_mission_status_ongoing = MissionStatus.objects.create(label="ongoing")
        self.test_mission_status_finish = MissionStatus.objects.create(label="finish")
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
            bearer_user=self.test_user_senior,
            status=self.test_mission_status_open,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission",
            description="description test mission"
        )
        self.test_mission2 = Mission.objects.create(
            bearer_user=self.test_user_senior,
            status=self.test_mission_status_open,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission2",
            description="description test mission2"
        )

    def test_mission_details_status_open_get_senior_with_applicant(self):
        uidb64_senior = urlsafe_base64_encode(force_bytes(self.test_user_senior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        uidb64_junior = urlsafe_base64_encode(force_bytes(self.test_user_junior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        post_args = {
            'message_content': "new message test",
        }
        self.client.login(username="junior@test.fr", password="test123+")
        self.client.post(reverse('message-conv', args=[uidb64_senior,]), post_args, HTTP_REFERER="mission")
        self.client.logout()
        
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.get(reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission.pk))]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test context content
        self.assertTrue(response.context['senior'])
        self.assertEqual(response.context['mission'], self.test_mission)
        self.assertTrue(len(response.context['applicants']) > 0)        
        for obj in response.context['applicants']:
            self.assertIn(obj['user'], (self.test_user_junior,))
            self.assertIn(obj['uid'], (uidb64_junior,))
            self.assertFalse(obj['bearer_respond'])

    def test_mission_details_status_ongoing_get_senior(self):
        self.test_mission.acceptor_user = self.test_user_junior
        self.test_mission.status = self.test_mission_status_ongoing
        self.test_mission.save()
        uidb64_junior = urlsafe_base64_encode(force_bytes(self.test_user_junior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.get(reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission.pk))]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test context content
        self.assertTrue(response.context['senior'])
        self.assertEqual(response.context['mission'], self.test_mission)
        self.assertEqual(response.context['acceptor_user'], self.test_user_junior)
        self.assertEqual(response.context['uid'], uidb64_junior)

    def test_mission_details_status_open_get_junior(self):
        test_message_form = UserMessageForm()
        uidb64_senior = urlsafe_base64_encode(force_bytes(self.test_user_senior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission2.pk))
        
        self.client.login(username="junior@test.fr", password="test123+")
        response = self.client.get(reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission2.pk))]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test context content
        self.assertFalse(response.context['senior'])
        self.assertEqual(response.context['mission'], self.test_mission2)
        self.assertEqual(response.context['uid'], uidb64_senior)
        self.assertEqual(response.context['form_id'], "send-message-form")
        self.assertEqual(response.context['form_action'], "message-conv")
        self.assertEqual(response.context['submit_button_label'], "Postuler")
        self.assertEqual(response.context['back_url_name'], "mission-board") 
        
        # Test form used is the right one
        self.assertEqual(
            response.context["form"].fields.keys(), test_message_form.fields.keys()
        )

    def test_mission_details_status_open_applied_get_junior(self):
        uidb64_senior = urlsafe_base64_encode(force_bytes(self.test_user_senior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission2.pk))
        
        self.client.login(username="junior@test.fr", password="test123+")
        post_args = {
            'message_content': "new message test",
        }
        self.client.post(reverse('message-conv', args=[uidb64_senior,]), post_args, HTTP_REFERER="mission")
        response = self.client.get(reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission2.pk))]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test context content
        self.assertFalse(response.context['senior'])
        self.assertEqual(response.context['mission'], self.test_mission2)
        self.assertEqual(response.context['uid'], uidb64_senior)
        self.assertTrue(response.context['has_apply'])

    def test_mission_details_status_ongoing_get_junior(self):
        self.test_mission.acceptor_user = self.test_user_junior
        self.test_mission.status = self.test_mission_status_ongoing
        self.test_mission.save()
        uidb64_acceptor = urlsafe_base64_encode(force_bytes(self.test_mission.bearer_user.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        
        self.client.login(username="junior@test.fr", password="test123+")
        response = self.client.get(reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission.pk))]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test context content
        self.assertFalse(response.context['senior'])
        self.assertEqual(response.context['mission'], self.test_mission)
        self.assertEqual(response.context['acceptor_user'], self.test_user_junior)
        self.assertEqual(response.context['uid'], uidb64_acceptor)


class MissionCreateTestCase(TestCase):
    def setUp(self):
        self.test_user_type_junior = UserType.objects.create(label="junior")
        self.test_user_type_senior = UserType.objects.create(label="senior")
        self.test_user_senior = CustomUser.objects.create_user(
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
        self.test_user_junior = CustomUser.objects.create_user(
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
        self.test_mission_status_open = MissionStatus.objects.create(label="open")
        self.test_mission_status_ongoing = MissionStatus.objects.create(label="ongoing")
        self.test_mission_status_finish = MissionStatus.objects.create(label="finish")
        self.test_mission_category = MissionCategory.objects.create(
            label="test_category", 
            base_reward_amount=100, 
            xp_amount=10
        )
        self.test_mission_bonus_reward = MissionBonusReward.objects.create(
            reward_amount=50,
            description="test bonus reward"
        )
        self.test_mission_duplicate = Mission.objects.create(
            bearer_user=self.test_user_senior,
            status=self.test_mission_status_open,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission dup",
            description="description test mission dup"
        )

    def test_mission_create_get(self):
        test_mission_form = CreateMissionForm(self.test_user_senior)

        self.client.login(username="senior@test.fr", password="test123+")
        response =  self.client.get(reverse('mission-create'))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/create.html")

        # Test context content
        self.assertEqual(response.context['form_id'], "create-mission-form")
        self.assertEqual(response.context['form_action'], "mission-create")
        self.assertEqual(response.context['submit_button_label'], "Créer mission") 
        
        # Test form used is the right one
        self.assertEqual(
            response.context["form"].fields.keys(), test_mission_form.fields.keys()
        )

    def test_mission_create_post_valid(self):
        senior_wallet = Wallet.objects.create(
            balance=200
        )
        self.test_user_senior.wallet = senior_wallet
        self.test_user_senior.save()

        post_args = {
            'mission_title': "test mission create title",
            'mission_description': "test mission create description",
            'mission_category': self.test_mission_category.pk,
            'mission_bonus_amount': 100,
            'mission_bonus_description': "test mission create bonus description"
        }

        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('mission-create'), post_args)

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('mission-board'))
        self.assertTemplateUsed(template_name="mission/board.html")        

        # Test new mission created
        last_mission = Mission.objects.last()
        self.assertEqual(self.test_user_senior, last_mission.bearer_user)
        self.assertEqual(post_args['mission_title'], last_mission.title)
        self.assertEqual(post_args['mission_description'], last_mission.description)
        self.assertEqual(post_args['mission_category'], last_mission.category.pk)
        self.assertEqual(post_args['mission_bonus_amount'], last_mission.bonus_reward.reward_amount)
        self.assertEqual(post_args['mission_bonus_description'], last_mission.bonus_reward.description)
        
        # Test messages not empty and messages content
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            "Mission créée avec succés. Elle sera disponible pour les utilisateurs une fois validée par un Administrateur"
        )    

    def test_mission_create_post_invalid_title(self):
        senior_wallet = Wallet.objects.create(
            balance=200
        )
        self.test_user_senior.wallet = senior_wallet
        self.test_user_senior.save()

        post_args = {
            'mission_title': "title test mission dup",
            'mission_description': "test mission create description",
            'mission_category': self.test_mission_category.pk,
            'mission_bonus_amount': 100,
            'mission_bonus_description': "test mission create bonus description"
        }

        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('mission-create'), post_args)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/create.html")

        # Test errors not empty and errors content
        self.assertTrue(len(response.context['errors']) > 0)
        for error in response.context['errors']:
            self.assertIn(error[0], ('mission_title', ))    

    def test_mission_create_post_invalid_balance(self):
        senior_wallet = Wallet.objects.create(
            balance=0
        )
        self.test_user_senior.wallet = senior_wallet
        self.test_user_senior.save()

        post_args = {
            'mission_title': "test mission create title",
            'mission_description': "test mission create description",
            'mission_category': self.test_mission_category.pk,
            'mission_bonus_amount': 100,
            'mission_bonus_description': "test mission create bonus description"
        }

        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('mission-create'), post_args)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="mission/create.html")

        # Test form error mission created
        errors = {
            ('balance', "Vous n'avez pas les fonds disponibles pour créer cette mission")
        }        
        self.assertEqual(response.context['errors'], errors)


class MissionManagementTestCase(TestCase):
    def setUp(self):
        self.test_message_status_created = UserMessageStatus.objects.create(label="created")
        self.test_user_type_junior = UserType.objects.create(label="junior")
        self.test_user_type_senior = UserType.objects.create(label="senior")
        self.test_user_senior = CustomUser.objects.create_user(
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
        self.test_user_junior = CustomUser.objects.create_user(
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
        self.test_mission_status_open = MissionStatus.objects.create(label="open")
        self.test_mission_status_ongoing = MissionStatus.objects.create(label="ongoing")
        self.test_mission_status_finish = MissionStatus.objects.create(label="finish")
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
            bearer_user=self.test_user_senior,
            status=self.test_mission_status_open,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission",
            description="description test mission"
        )
        self.test_mission2 = Mission.objects.create(
            bearer_user=self.test_user_senior,
            acceptor_user=self.test_user_junior,
            status=self.test_mission_status_ongoing,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            title="title test mission2",
            description="description test mission2",
            acceptor_validate=True
        )

    def test_mission_management_accept_user_post(self):
        uidb64_junior = urlsafe_base64_encode(force_bytes(self.test_user_junior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        post_args = {
            'action': "accept"
        }
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('mission-manage', args=[uidb64_junior,]), post_args)

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission.pk))]))
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test data changes on mission
        # self.assertEqual(self.test_mission.acceptor_user, self.test_user_junior)
        # self.assertEqual(self.test_mission.status, self.test_mission_status_ongoing)
        
        # Test messages not empty and messages content
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            "Utilisateur {} {} accepté pour la mission".format(self.test_user_junior.first_name, self.test_user_junior.last_name)
        ) 

    def test_mission_management_validate_mission_post(self):
        uidb64_junior = urlsafe_base64_encode(force_bytes(self.test_user_junior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission.pk))
        post_args = {
            'action': "end"
        }
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('mission-manage', args=[uidb64_junior,]), post_args)

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission.pk))]))
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test data changes on mission
        # self.assertTrue(self.test_mission.bearer_validate) 

    def test_mission_management_end_mission_post(self):
        junior_wallet = Wallet.objects.create(
            balance=0
        )
        self.test_user_junior.wallet = junior_wallet
        self.test_user_junior.save()
        
        uidb64_junior = urlsafe_base64_encode(force_bytes(self.test_user_junior.pk)) + "-" + urlsafe_base64_encode(force_bytes(self.test_mission2.pk))
        post_args = {
            'action': "end"
        }
        self.client.login(username="senior@test.fr", password="test123+")
        response = self.client.post(reverse('mission-manage', args=[uidb64_junior,]), post_args)

        # Test status_code/redirection and template used
        self.assertRedirects(response=response, expected_url=reverse('mission-details', args=[urlsafe_base64_encode(force_bytes(self.test_mission2.pk))]))
        self.assertTemplateUsed(template_name="mission/details.html")

        # Test data changes on mission
        # self.assertTrue(self.test_mission2.acceptor_validate)
        # self.assertEqual(self.test_mission2.status, self.test_mission_status_finish)
        # self.assertTrue(self.test_user_junior.wallet.balance > 0)
        # self.assertTrue(self.test_user_junior.experience_point > 0)



