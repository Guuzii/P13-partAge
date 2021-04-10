from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from messaging.models.message_status import UserMessageStatus


class Command(BaseCommand):
    help = "Insert datas in messaging ref tables - Defining MESSAGE_STATUS with corresponding datas in settings of the project is required"

    def handle(self, *args, **options):
        self.stdout.write("----------------- START UPDATES ON messaging -----------------")

        if (settings.MESSAGE_STATUS is None):
            raise CommandError('MESSAGE_STATUS not found in settings')
        for message_status in settings.MESSAGE_STATUS:
            if not UserMessageStatus.objects.filter(label__iexact=message_status):
                new_message_status = UserMessageStatus(label=message_status)
                new_message_status.save()
                self.stdout.write("Adding new message status into database : {}".format(new_message_status))
            else:
                self.stdout.write("Existing message status : {}".format(message_status))

        self.stdout.write("----------------- END UPDATES ON messaging -----------------")
