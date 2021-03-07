from django.test import TestCase

from unittest.mock import Mock, patch

from user.management.commands.update_user_refs import Command


class CommandTest(TestCase):
    @patch('user.management.commands.update_user_refs.Command.handle')
    def test_custom_command_update_user_refs(self, mock_get):
        user_type = {
            'label': "senior",
        }
        document_type = {
            'label': "identity",
        }

        values = [user_type, document_type,]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = values
        
        response = Command.handle(self)
        
        self.assertIsNotNone(response)
        self.assertTrue(mock_get.called)