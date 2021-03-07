from django.test import TestCase

from user.models.custom_user import CustomUser
from user.models.document_type import DocumentType
from user.models.document import Document
from user.models.user_type import UserType
from user.models.wallet import Wallet


class walletModelTestCase(TestCase):
    def setUp(self):
        self.new_test_wallet = Wallet.objects.create()

    def test_wallet_model(self):
        # Test wallet is created
        self.assertIsNotNone(self.new_test_wallet)

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_wallet), str(self.new_test_wallet.balance))

        # Test created wallet datas
        self.assertEqual(self.new_test_wallet.balance, 0)


class userTypeModelTestCase(TestCase):
    def setUp(self):
        self.new_test_user_type = UserType.objects.create(
            label="test_user_type"
        )

    def test_user_type_model(self):
        # Test user type is created
        self.assertIsNotNone(self.new_test_user_type)

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_user_type), self.new_test_user_type.label)

        # Test created user type datas
        self.assertEqual(self.new_test_user_type.label, "test_user_type")


class CustomUserModelTestCase(TestCase):
    def setUp(self):
        self.new_test_user = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            is_superuser=False
        )
        self.new_test_admin_user = CustomUser.objects.create_superuser(
            first_name="testeurAdmin",
            last_name="testAdmin",
            email="testadmin@test.fr",
            birthdate="1900-01-02",
            password="test123456+",
        )
        
    def test_custom_user_model(self):
        # Test user is created
        self.assertIsNotNone(self.new_test_user)
        self.assertEqual(self.new_test_user.email, "test@test.fr")

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_user), self.new_test_user.email)

        # Test created user datas
        self.assertEqual(self.new_test_user.first_name, "testeur")
        self.assertEqual(self.new_test_user.last_name, "test")
        self.assertEqual(self.new_test_user.birthdate, "1900-01-01")
        self.assertIsNotNone(self.new_test_user.wallet)
        self.assertIsNone(self.new_test_user.user_type)
        self.assertFalse(self.new_test_user.is_superuser)
        self.assertFalse(self.new_test_user.is_admin)
        self.assertFalse(self.new_test_user.is_staff)
        self.assertFalse(self.new_test_user.is_active)
        self.assertFalse(self.new_test_user.email_validated)

    def test_custom_admin_user_model(self):
        # Test admin user is created
        self.assertIsNotNone(self.new_test_admin_user)
        self.assertEqual(self.new_test_admin_user.email, "testadmin@test.fr")

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_admin_user), self.new_test_admin_user.email)

        # Test created admin user datas
        self.assertEqual(self.new_test_admin_user.first_name, "testeurAdmin")
        self.assertEqual(self.new_test_admin_user.last_name, "testAdmin")
        self.assertEqual(self.new_test_admin_user.birthdate, "1900-01-02")
        self.assertIsNone(self.new_test_admin_user.wallet)
        self.assertIsNone(self.new_test_admin_user.user_type)
        self.assertTrue(self.new_test_admin_user.is_superuser)
        self.assertTrue(self.new_test_admin_user.is_admin)
        self.assertTrue(self.new_test_admin_user.is_staff)
        self.assertTrue(self.new_test_admin_user.is_active)
        self.assertTrue(self.new_test_admin_user.email_validated)


class documentTypeModelTestCase(TestCase):
    def setUp(self):
        self.new_test_document_type = DocumentType.objects.create(
            label="test_doc_type"
        )

    def test_document_type_model(self):
        # Test document type is created
        self.assertIsNotNone(self.new_test_document_type)

        # Test model __str__ returnd value
        self.assertEqual(str(self.new_test_document_type), self.new_test_document_type.label)

        # Test created document type datas
        self.assertEqual(self.new_test_document_type.label, "test_doc_type")


class documentModelTestCase(TestCase):
    def setUp(self):
        self.test_user = CustomUser.objects.create_user(
            first_name="testeur",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            is_superuser=False
        )
        self.test_document_type = DocumentType.objects.create(
            label="test_doc_type"
        )
        self.test_document = Document.objects.create(
            created_at="1900-01-01",
            path="static/path/to/document",
            user=self.test_user,
            document_type=self.test_document_type
        )

    def test_document_model(self):
        # Test document is created
        self.assertIsNotNone(self.test_document)

        # Test model __str__ returnd value
        self.assertEqual(str(self.test_document), self.test_document.document_type.label)

        # Test created document datas
        self.assertEqual(self.test_document.created_at, "1900-01-01")
        self.assertEqual(self.test_document.path, "static/path/to/document")
        self.assertEqual(self.test_document.user.pk, self.test_user.pk)
        self.assertEqual(self.test_document.document_type.pk, self.test_document_type.pk)
