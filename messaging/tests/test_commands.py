from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.conf import settings


class CommandUpdateRefsMessagingTest(TestCase):
    def test_custom_command_update_refs_messaging(self):
        out = StringIO()
        call_command('update_refs_messaging', stdout=out)
        out_value = out.getvalue()

        self.assertIn('START UPDATES ON messaging', out.getvalue())
        self.assertIn('END UPDATES ON messaging', out.getvalue())

        for message_status in settings.MESSAGE_STATUS:
            self.assertIn(message_status, out.getvalue())
