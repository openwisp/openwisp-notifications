from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class EmailTokenGenerator(PasswordResetTokenGenerator):
    """
    Email token generator that extends the default PasswordResetTokenGenerator
    with a fixed 7-day expiry period and a salt key.
    """

    key_salt = "openwisp_notifications.tokens.EmailTokenGenerator"

    def __init__(self):
        super().__init__()
        self.expiry_days = 7

    def check_token(self, user, token):
        """
        Check that a token is correct for a given user and has not expired.
        """
        if not (user and token):
            return False

        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                self._make_token_with_timestamp(user, ts, secret),
                token,
            ):
                break
        else:
            return False

        # Check the timestamp is within the expiry limit.
        if (self._num_seconds(self._now()) - ts) > self._expiry_seconds():
            return False

        return True

    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and password to produce a token that is
        invalidated when the password is reset.
        """
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, "") or ""
        return f"{user.pk}{user.password}{timestamp}{email}"

    def _expiry_seconds(self):
        """
        Returns the number of seconds representing the token's expiry period.
        """
        return self.expiry_days * 24 * 3600


email_token_generator = EmailTokenGenerator()
