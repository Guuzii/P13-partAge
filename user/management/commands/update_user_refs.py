from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from datetime import datetime

from user.models.user_type import UserType
from user.models.document_type import DocumentType


class Command(BaseCommand):
    help = "Insert datas in ref tables - Require to define tuples with corresponding datas in settings of the project"

    def handle(self, *args, **options):
        print("**************************************************")
        print("START DATABASE_UPDATE - {}".format(datetime.now()))
        print("**************************************************")

        for user_type in settings.USER_TYPES:
            if not UserType.objects.filter(label__iexact=user_type):
                new_user_type = UserType(label=user_type)
                new_user_type.save()
                print("Adding new user type into database :", new_user_type)
            else:
                print("Existing user type :", user_type)

        for document_type in settings.DOCUMENT_TYPES:
            if not DocumentType.objects.filter(label__iexact=document_type):
                new_document_type = DocumentType(label=document_type)
                new_document_type.save()
                print("Adding new document type into database :", new_document_type)
            else:
                print("Existing document type :", document_type)
        

        self.stdout.write("----------------- REFS IMPORTS DONE -----------------")

