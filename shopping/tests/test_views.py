import json

from django.core import serializers
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Q
from django.middleware.csrf import get_token

from shopping.models.product_transaction import ProductTransaction
from shopping.models.product import Product

from user.models.user_type import UserType
from user.models.custom_user import CustomUser
from user.models.wallet import Wallet

class ShoppingProductsTestCase(TestCase):
    def setUp(self):
        self.test_user_type_junior = UserType.objects.create(label="junior")
        self.test_user_type_senior = UserType.objects.create(label="senior")
        self.test_wallet = Wallet.objects.create(balance=1000)
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
            user_type=self.test_user_type_junior,
        )
        self.test_user_junior.wallet = self.test_wallet
        self.test_user_junior.save()
        self.test_product_multiple = Product.objects.create(
            label="test product multiple",
            description="test product multiple description",
            price=200,
            xp_amount=20,
            is_multiple=True
        )
        self.test_product_unique = Product.objects.create(
            label="test product unique",
            description="test product unique description",
            price=500,
            xp_amount=50,
        )

    def test_shopping_product_get_junior(self):
        self.client.login(username="junior@test.fr", password="test123+")
        response = self.client.get(reverse('shopping-products'))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="shopping/products.html")

        # Test context datas
        self.assertTrue(response.context['junior'])

        # Test product list in context contains all products
        self.assertTrue(len(response.context['products']) > 0)
        for product in response.context['products']:
            self.assertIn(product.pk, (self.test_product_multiple.pk, self.test_product_unique.pk))
        
        new_transaction = ProductTransaction(
            user=self.test_user_junior,
            product=self.test_product_unique
        )
        new_transaction.save()

        response = self.client.get(reverse('shopping-products'))

        # Test product list in context contains all products except unique ones the user buyed
        self.assertTrue(len(response.context['products']) > 0)
        for product in response.context['products']:
            self.assertNotIn(product.pk, (self.test_product_unique.pk,))

    def test_shopping_product_get_balance(self):
        self.client.login(username="junior@test.fr", password="test123+")
        url = reverse('shopping-products') + '?balance=1'
        response = self.client.get(url)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="shopping/products.html")

        # Test response content
        self.assertEqual(int(response.content.decode('utf8')), self.test_user_junior.wallet.balance)

    def test_shopping_product_get_history(self):
        self.client.login(username="junior@test.fr", password="test123+")
        url = reverse('shopping-products') + '?history=1'
        
        new_transaction = ProductTransaction(
            user=self.test_user_junior,
            product=self.test_product_unique
        )
        new_transaction.save()

        response = self.client.get(url)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="shopping/products.html")

        # Test response json
        transaction_json = [{
            'product': serializers.serialize('json', (new_transaction.product,)),
            'transaction': serializers.serialize('json', (new_transaction,))
        }]
        self.assertJSONEqual(response.content.decode('utf8'), transaction_json)

    def test_shopping_product_get_refresh(self):
        self.client.login(username="junior@test.fr", password="test123+")
        url = reverse('shopping-products') + '?refresh=1'
        response = self.client.get(url)

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="shopping/products.html")

        # Test response json
        products = Product.objects.all()
        products_json = serializers.serialize('json', products)
        self.assertJSONEqual(json.loads(response.content), products_json)

    def test_shopping_product_post_junior(self):
        self.client.login(username="junior@test.fr", password="test123+")
        product_pk = self.test_product_multiple.pk
        response = self.client.post(reverse('shopping-products-buy', args=[product_pk,]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="shopping/products.html")

        # Test response json
        updated_user = CustomUser.objects.get(pk=self.test_user_junior.pk)
        response_json = {
            'message': "Vous avez acheté le produit : '{}'".format(self.test_product_multiple),
            'valid': True,
            'is_unique': not self.test_product_multiple.is_multiple,
            'new_balance': updated_user.wallet.balance
        }
        self.assertEqual(json.loads(response.content), response_json)

    def test_shopping_product_post_junior_error_balance(self):
        self.test_user_junior.wallet.balance = 0
        self.test_user_junior.wallet.save()
        self.client.login(username="junior@test.fr", password="test123+")
        product_pk = self.test_product_unique.pk
        response = self.client.post(reverse('shopping-products-buy', args=[product_pk,]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name="shopping/products.html")

        # Test response json
        response_json = {
            'message': "Vous n'avez pas les fonds nécessaires pour acheter ce produit : '{}'".format(self.test_product_unique),
            'valid': False
        }
        self.assertEqual(json.loads(response.content), response_json)        

    def test_shopping_product_post_not_junior(self):
        self.client.login(username="senior@test.fr", password="test123+")
        product_pk = self.test_product_unique.pk
        response = self.client.post(reverse('shopping-products-buy', args=[product_pk,]))

        # Test status_code/redirection and template used
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(template_name="shopping/products.html")

        # Test response json
        url_redirect = reverse("shopping-products")
        self.assertEqual(response.content.decode('utf8'), url_redirect)
