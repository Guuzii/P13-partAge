from django.contrib import admin

from shopping.models.product import Product
from shopping.models.product_transaction import ProductTransaction


class CustomProductAdmin(admin.ModelAdmin):
    list_display = ('label', 'description', 'price', 'xp_amount', 'path_to_sprite', 'is_multiple')
    list_filter = ('is_multiple',)
    search_fields = ('label', 'path_to_sprite')


class CustomProductTransactionAdmin(admin.ModelAdmin):  
    list_display = ('product', 'user', 'created_at')
    list_filter = ('product', 'created_at',)
    search_fields = ('product', 'user')
    readonly_fields = ['product', 'user', 'created_at']
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False


admin.site.register(Product, CustomProductAdmin)
admin.site.register(ProductTransaction, CustomProductTransactionAdmin)
