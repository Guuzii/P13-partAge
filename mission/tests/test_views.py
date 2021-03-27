import json

from django.core import serializers
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from user.models.user_type import UserType
from user.models.custom_user import CustomUser


class MissionBoardTestCase(TestCase):
    def setUp(self):
        self.test_user_type_junior = UserType.objects.create(
            label="junior"
        )
        self.test_user_type_senior = UserType.objects.create(
            label="senior"
        )
        self.test_user_senior = CustomUser.objects.create_user(
            first_name="test",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_user_senior.user_type = self.test_user_type_senior
        self.test_user_junior = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="testeur@test.fr",
            birthdate="1910-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_user_junior.user_type = self.test_user_type_junior
        self.test_user_type_junior.save()
        self.test_user_type_senior.save()
