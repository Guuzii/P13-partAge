from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.conf import settings


class CommandUpdateRefsUserTest(TestCase):
    def test_custom_command_update_refs_user(self):
        out = StringIO()
        call_command('update_refs_user', stdout=out)
        out_value = out.getvalue()

        self.assertIn('START UPDATES ON user', out.getvalue())
        self.assertIn('END UPDATES ON user', out.getvalue())

        for user_type in settings.USER_TYPES:
            self.assertIn(user_type, out.getvalue())

        for document_type in settings.DOCUMENT_TYPES:
            self.assertIn(document_type, out.getvalue())


class CommandUpdateRefsTest(TestCase):
    def test_custom_command_update_refs_all(self):
        out = StringIO()
        call_command('update_refs', 'all', stdout=out)
        out_value = out.getvalue()

        self.assertIn('START DATABASE_UPDATE FOR - all -', out.getvalue())
        self.assertIn('REFS UPDATES FOR all - DONE', out.getvalue())
    