from django.test import TestCase
from django.utils.timezone import now

from shopping.models.product_transaction import ProductTransaction
from shopping.models.product import Product

from user.models.custom_user import CustomUser


class ShoppingProductTransactionModelTestCase(TestCase):
    def setUp(self):
        self.test_user = CustomUser.objects.create_user(
            first_name="test",
            last_name="test",
            email="test@test.fr",
            birthdate="1900-01-01",
            password="test123+",
            email_validated=True,
            is_active=True,
            is_superuser=False
        )
        self.test_product = Product.objects.create(
            label="test product",
            description="test product description",
            price=200,
            is_multiple=True
        )
        self.new_product_transaction = ProductTransaction.objects.create(
            user=self.test_user,
            product=self.test_product
        )

    def test_product_transaction_model(self):
        # Test product transaction is created
        self.assertIsNotNone(self.new_product_transaction)

        # Test model __str__ returned value
        self.assertEqual(str(self.new_product_transaction), self.test_product.label)

        # Test created product transaction datas
        self.assertEqual(self.new_product_transaction.user, self.test_user)
        self.assertEqual(self.new_product_transaction.product, self.test_product)


class ShoppingProductModelTestCase(TestCase):
    def setUp(self):
        self.new_test_product = Product.objects.create(
            label="test product",
            description="test product description",
            price=200,
            xp_amount=20,
            is_multiple=True
        )

    def test_product_model(self):
        # Test product transaction is created
        self.assertIsNotNone(self.new_test_product)

        # Test model __str__ returned value
        self.assertEqual(str(self.new_test_product), self.new_test_product.label)

        # Test created product transaction datas
        self.assertEqual(self.new_test_product.label, "test product")
        self.assertEqual(self.new_test_product.description, "test product description")
        self.assertEqual(self.new_test_product.price, 200)
        self.assertEqual(self.new_test_product.xp_amount, 20)
        self.assertIsNone(self.new_test_product.path_to_sprite)
        self.assertTrue(self.new_test_product.is_multiple)
