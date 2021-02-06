from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# Create your models here.

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, first_name, last_name, email, birthdate, password, **extra_fields):
        """
        Creates and saves a User with the given first_name, last_name, email, date of
        birth and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not first_name:
            raise ValueError(_('Users must have a first name'))
        if not last_name:
            raise ValueError(_('Users must have a last name'))
        if not birthdate:
            raise ValueError(_('Users must have a date of birth'))

        if not extra_fields['is_superuser']:
            wallet = Wallet()
            wallet.save()
        else:
            wallet = None

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email),
            birthdate=birthdate,
            id_wallet=wallet,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user


    def create_superuser(self, first_name, last_name, email, birthdate, password, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('email_validated', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if extra_fields.get('is_admin') is not True:
            raise ValueError(_('Superuser must have is_admin=True.'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))

        return self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            birthdate=birthdate,
            password=password,
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        verbose_name=_('First name'),
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name=_('Last name'),
        max_length=150,
    )
    email = models.EmailField(
        verbose_name=_('Email address'),
        max_length=255,
        unique=True,
    )
    birthdate = models.DateField(
        verbose_name=_('Date of birth'),
    )
    created_at = models.DateField(
        verbose_name=_('User creation date'),
        default=timezone.now
    )
    experience_point = models.IntegerField(
        verbose_name=_("Experience points"),
        default=0
    )
    email_validated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)    

    id_wallet = models.ForeignKey('user.Wallet', null=True, on_delete=models.PROTECT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birthdate',]

    objects = CustomUserManager()

    class Meta:
        db_table  = 'user_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email


class Wallet(models.Model):
    balance = models.IntegerField(
        verbose_name=_('Wallet balance'),
        default=0
    )

    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')

    def __str__(self):
        return self.balance


class Document(models.Model):
    created_at = models.DateField(
        verbose_name=_('Document creation date'),
        default=timezone.now
    )
    path = models.CharField(
        verbose_name=_('Path to file'),
        max_length=150,
    )
    is_valid = models.BooleanField(default=False)

    id_user = models.ForeignKey('user.Wallet', on_delete=models.CASCADE)
    id_type = models.ForeignKey('user.DocumentType', on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def __str__(self):
        return self.path


class DocumentType(models.Model):
    label = models.CharField(
        verbose_name=_('Document type label'),
        max_length=30
    )

    class Meta:
        db_table  = 'user_ref_document_type'
        verbose_name = _('Document type')
        verbose_name_plural = _('Document types')

    def __str__(self):
        return self.label
