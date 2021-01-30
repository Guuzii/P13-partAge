# from django.db import models

# # Create your models here.

# from django.db import models
# from django.contrib.auth.models import (
#     BaseUserManager, AbstractBaseUser
# )


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, date_of_birth, password=None):
#         """
#         Creates and saves a User with the given email, date of
#         birth and password.
#         """
#         if not email:
#             raise ValueError('Users must have an email address')

#         user = self.model(
#             email=self.normalize_email(email),
#             date_of_birth=date_of_birth,
#         )

#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, date_of_birth, password=None):
#         """
#         Creates and saves a superuser with the given email, date of
#         birth and password.
#         """
#         user = self.create_user(
#             email,
#             password=password,
#             date_of_birth=date_of_birth,
#         )
#         user.is_admin = True
#         user.save(using=self._db)
#         return user


# class CustomUser(AbstractBaseUser):
#     first_name = models.CharField(
#         verbose_name='Prénom',
#         max_length=150,
#     )
#     last_name = models.CharField(
#         verbose_name='Nom',
#         max_length=150,
#     )
#     email = models.EmailField(
#         verbose_name='Adresse email',
#         max_length=255,
#         unique=True,
#     )
#     birthdate = models.DateField(
#         verbose_name='Date de naissance',
#     )
#     is_active = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name', 'last_name', 'birthdate',]

#     def __str__(self):
#         return self.email