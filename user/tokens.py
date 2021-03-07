from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

from user.models.custom_user import CustomUser


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) +
            text_type(user.email_validated)
        )


class PasswordResetToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) +
            text_type(user.reset_password)
        )


account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetToken()