from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.utils.timezone import now
from django.middleware.csrf import get_token

from shopping.models.product_transaction import ProductTransaction
from shopping.models.product import Product

from user.models.user_type import UserType
from user.models.custom_user import CustomUser


class ShoppingProducts(View):
    template_name = 'shopping/products.html'
    context = {
        'title': _("PRODUITS"),
    }    

    def get(self, request):
        junior_type = UserType.objects.get(label__iexact="junior")

        if (request.user.is_authenticated and request.user.user_type == junior_type):
            if (request.GET.get('csrf')):
                return JsonResponse(get_token(request), safe=False)

            if (request.GET.get('balance')):
                return JsonResponse(request.user.wallet.balance, safe=False)

            if (request.GET.get('history')):
                user_transactions = ProductTransaction.objects.filter(user=request.user).order_by("-created_at")
                user_transactions_with_products = []

                for transaction in user_transactions:
                    user_transactions_with_products.append({
                        'product': serializers.serialize('json', (transaction.product,)),
                        'transaction': serializers.serialize('json', (transaction,))
                    })

                return JsonResponse(user_transactions_with_products, safe=False)

            self.context['junior'] = True

            user_transaction_unique_products = ProductTransaction.objects.filter(Q(user=request.user) & Q(product__is_multiple=False))
            user_unique_products_pk = []
            for transaction in user_transaction_unique_products:
                user_unique_products_pk.append(transaction.product.pk)

            products = Product.objects.exclude(pk__in=user_unique_products_pk).order_by('price')            

            if (request.GET.get('refresh')):
                products_json = serializers.serialize('json', products)
                return JsonResponse(products_json, safe=False)

            self.context['products'] = products
        else:
            self.context['junior'] = False
            products = Product.objects.all().order_by('price')

            self.context['products'] = products            

        return render(request, self.template_name, self.context)

    def post(self, request, product_pk):
        junior_type = UserType.objects.get(label__iexact="junior")

        if (request.user.is_authenticated and request.user.user_type == junior_type):
            selected_product = Product.objects.get(pk=int(product_pk))

            if (int(request.user.wallet.balance) < int(selected_product.price)):
                response = {
                    'message': "Vous n'avez pas les fonds nécessaires pour acheter ce produit : '{}'".format(selected_product),
                    'valid': False
                }
            else:
                new_transaction = ProductTransaction(
                    user=request.user,
                    product=selected_product
                )
                new_transaction.save()

                request.user.wallet.balance -= selected_product.price
                request.user.wallet.save()

                response = {
                    'message': "Vous avez acheté le produit : '{}'".format(selected_product),
                    'valid': True,
                    'is_unique': not selected_product.is_multiple,
                    'new_balance': request.user.wallet.balance
                }

            return JsonResponse(response, safe=False)
        else:
            messages.error(
                request, 
                message=_("Vous devez être authentifié et avoir un type utilisateur = Junior pour acheter un produit de la boutique"),
                extra_tags="alert-danger"
            )            
            return HttpResponse(reverse('shopping-products'), status=403)

