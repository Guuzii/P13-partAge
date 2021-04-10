from django.test import TestCase
from django.utils.timezone import now

from mission.models.mission_status import MissionStatus
from mission.models.mission_category import MissionCategory
from mission.models.mission_bonus_reward import MissionBonusReward
from mission.models.mission import Mission

from user.models.custom_user import CustomUser


class MissionStatusModelTestCase(TestCase):
    def setUp(self):
        self.new_test_mission_status = MissionStatus.objects.create(
            label="test_mission_status"
        )

    def test_mission_status_model(self):
        # Test mission status is created
        self.assertIsNotNone(self.new_test_mission_status)

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_mission_status), self.new_test_mission_status.label)

        # Test created mission status datas
        self.assertEqual(self.new_test_mission_status.label, "test_mission_status")


class MissionCategoryModelTestCase(TestCase):
    def setUp(self):
        self.new_test_mission_category = MissionCategory.objects.create(
            label="test_mission_category",
            base_reward_amount=200,
            xp_amount=20
        )

    def test_mission_category_model(self):
        # Test mission category is created
        self.assertIsNotNone(self.new_test_mission_category)

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_mission_category), self.new_test_mission_category.label)

        # Test created mission category datas
        self.assertEqual(self.new_test_mission_category.label, "test_mission_category")
        self.assertEqual(self.new_test_mission_category.base_reward_amount, 200)
        self.assertEqual(self.new_test_mission_category.xp_amount, 20)


class MissionBonusRewardModelTestCase(TestCase):
    def setUp(self):
        self.new_test_mission_bonus = MissionBonusReward.objects.create(
            reward_amount=100,
            description="test bonus reward"
        )

    def test_mission_bonus_reward_model(self):
        # Test mission bonus reward is created
        self.assertIsNotNone(self.new_test_mission_bonus)

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_mission_bonus), self.new_test_mission_bonus.description)

        # Test created mission bonus reward datas
        self.assertEqual(self.new_test_mission_bonus.reward_amount, 100)
        self.assertEqual(self.new_test_mission_bonus.description, "test bonus reward")


class MissionModelTestCase(TestCase):
    def setUp(self):
        self.test_bearer_user = CustomUser.objects.create_user(
            first_name="test",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_mission_status = MissionStatus.objects.create(
            label="test_mission_status"
        )
        self.test_mission_category = MissionCategory.objects.create(
            label="test_mission_category",
            base_reward_amount=200,
            xp_amount=20
        )
        self.test_mission_bonus_reward = MissionBonusReward.objects.create(
            reward_amount=100,
            description="test bonus reward"
        )
        self.date_now = now()

    def test_mission_model(self):
        new_mission = Mission.objects.create(
            bearer_user=self.test_bearer_user,
            status=self.test_mission_status,
            category=self.test_mission_category,
            bonus_reward=self.test_mission_bonus_reward,
            created_at=self.date_now,
            title="test mission title",
            description="test mission description",
        )

        # Test mission is created
        self.assertIsNotNone(new_mission)

        # Test model __str__ returned value
        self.assertEqual(str(new_mission), new_mission.title)

        # Test created mission datas
        self.assertEqual(new_mission.created_at, self.date_now)
        self.assertEqual(new_mission.bearer_user, self.test_bearer_user)
        self.assertEqual(new_mission.status, self.test_mission_status)
        self.assertEqual(new_mission.category, self.test_mission_category)
        self.assertEqual(new_mission.bonus_reward, self.test_mission_bonus_reward)
        self.assertEqual(new_mission.title, 'test mission title')
        self.assertEqual(new_mission.description, 'test mission description')
