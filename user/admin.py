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

    # def has_add_permission(request):
    #     return False


class CustomUserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('first_name', 'last_name', 'email', 'birthdate', 'created_at', 'is_active', 'email_validated',)
    list_filter = ('is_active', 'email_validated',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'email_validated', 'is_active', 'wallet',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'birthdate', 'user_type',)}),
    )
    inlines = [UserDocuments,]
    readonly_fields = ['email_validated', 'wallet']
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
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

# unregister the Group model from admin.
admin.site.unregister(Group)
