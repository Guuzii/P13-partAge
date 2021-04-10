from django.test import TestCase
from django.utils.timezone import now

from messaging.models.message import UserMessage
from messaging.models.message_status import UserMessageStatus

from user.models.custom_user import CustomUser


class UserMessageStatusModelTestCase(TestCase):
    def setUp(self):
        self.new_test_message_status = UserMessageStatus.objects.create(
            label="test_message_status"
        )

    def test_user_message_status_model(self):
        # Test message status is created
        self.assertIsNotNone(self.new_test_message_status)

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_message_status), self.new_test_message_status.label)

        # Test created message status datas
        self.assertEqual(self.new_test_message_status.label, "test_message_status")


class UserMessageModelTestCase(TestCase):
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
        self.date_now = now()

    def test_user_message_model(self):
        new_message = UserMessage(
            sender_user=self.test_user_1,
            receiver_user=self.test_user_2,
            status=self.test_message_status,
            created_at=self.date_now,
            content='content message test model'
        )

        # Test message is created
        self.assertIsNotNone(new_message)

        # Test model __str__ returned value
        self.assertEqual(str(new_message), new_message.content)

        # Test created message datas
        self.assertEqual(new_message.created_at, self.date_now)
        self.assertEqual(new_message.sender_user, self.test_user_1)
        self.assertEqual(new_message.receiver_user, self.test_user_2)
        self.assertEqual(new_message.content, 'content message test model')
