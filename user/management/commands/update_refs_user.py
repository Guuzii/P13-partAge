from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from datetime import datetime

from user.models.user_type import UserType
from user.models.document_type import DocumentType


class Command(BaseCommand):
    help = "Insert datas in user ref tables - Defining tuples USER_TYPES and DOCUMENT_TYPES with corresponding datas in settings of the project is required"

    def handle(self, *args, **options):
        self.stdout.write("----------------- START UPDATES ON user -----------------")

        if (settings.USER_TYPES is None):
            raise CommandError('USER_TYPES not found in settings')
        for user_type in settings.USER_TYPES:
            if not UserType.objects.filter(label__iexact=user_type):
                new_user_type = UserType(label=user_type)
                new_user_type.save()
                self.stdout.write("Adding new user type into database : {}".format(new_user_type))
            else:
                self.stdout.write("Existing user type : {}".format(user_type))

        if (settings.DOCUMENT_TYPES is None):
            raise CommandError('DOCUMENT_TYPES not found in settings')
        for document_type in settings.DOCUMENT_TYPES:
            if not DocumentType.objects.filter(label__iexact=document_type):
                new_document_type = DocumentType(label=document_type)
                new_document_type.save()
                self.stdout.write("Adding new document type into database : {}".format(new_document_type))
            else:
                self.stdout.write("Existing document type : {}".format(document_type))

        self.stdout.write("----------------- END UPDATES ON user -----------------")
