from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.conf import settings
from django.urls import reverse

from user.models.custom_user import CustomUser
from user.models.document import Document
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm
)

# Register your models here.
class UserDocuments(admin.TabularInline):    
    model = Document  # the query goes through an intermediate table.
    extra = 1
    verbose_name = "Document"
    verbose_name_plural = "Documents"
    readonly_fields = ['created_at', 'path', 'document_type',]

    def view_on_site(self, obj):
        return settings.BASE_URL + obj.path

class CustomUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = CustomUserChangeForm
    # add_form = CustomUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('first_name', 'last_name', 'email', 'birthdate', 'created_at', 'is_active', 'email_validated',)
    list_filter = ('is_active', 'email_validated',)
    fieldsets = (
        ('Credentials', {'fields': ('email', 'password', 'email_validated', 'is_active')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'birthdate', 'user_type',)}),
    )
    inlines = [UserDocuments,]
    readonly_fields = ['email_validated',]
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




# Now register the new UserAdmin...
admin.site.register(CustomUser, CustomUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)
