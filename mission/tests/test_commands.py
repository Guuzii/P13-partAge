from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.conf import settings


class CommandUpdateRefsMessagingTest(TestCase):
    def test_custom_command_update_refs_messaging(self):
        out = StringIO()
        call_command('update_refs_messaging', stdout=out)
        out_value = out.getvalue()

        self.assertIn('START UPDATES ON mission', out.getvalue())
        self.assertIn('END UPDATES ON mission', out.getvalue())

        for mission_status in settings.MISSION_STATUS:
            self.assertIn(mission_status, out.getvalue())

        for mission_category in settings.MISSION_CATEGORY:
            self.assertIn(mission_category['label'], out.getvalue())
