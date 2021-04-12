from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.conf import settings
from django.urls import reverse

from user.models.custom_user import CustomUser
from user.models.user_type import UserType
from user.models.document import Document
from user.models.document_type import DocumentType
from user.models.wallet import Wallet

from user.forms import CustomUserCreationForm, CustomUserChangeForm

class UserDocuments(admin.TabularInline):    
    model = Document
    extra = 0
    verbose_name = "Document"
    verbose_name_plural = "Documents"
    readonly_fields = ['created_at', 'path', 'document_type',]

    def view_on_site(self, obj):
        return settings.BASE_URL + obj.path

    def has_add_permission(self, request, obj=None):
        return False


class UserWallet(admin.TabularInline):
    model = CustomUser
    fieldsets = (
        ('Utilisateur', {'fields': ('first_name', 'last_name', 'email',)}),
    )
    readonly_fields = ['first_name', 'last_name', 'email',]
    extra = 0
    verbose_name = "User"
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CustomUserWallet(admin.ModelAdmin):
    list_display = ('pk', 'balance',)
    readonly_fields = ['pk',]
    search_fields = ('pk',)
    ordering = ('pk',)
    inlines = [UserWallet,]
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'email', 'birthdate', 'created_at', 'is_active', 'email_validated', 'reset_password')
    list_filter = ('is_active', 'email_validated',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'email_validated', 'is_active','reset_password', 'wallet',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'birthdate', 'user_type',)}),
    )
    inlines = [UserDocuments,]
    readonly_fields = ['email_validated', 'wallet']    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'birthdate', 'password1', 'password2'),
        }),
    )
    search_fields = ('first_name', 'last_name','email')
    ordering = ('created_at',)
    filter_horizontal = ()

    class Media:
        css = {
            'all': ('platform/css/admin-styles.css',)
        }


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Wallet, CustomUserWallet)

# unregister the Group model from admin.
admin.site.unregister(Group)
