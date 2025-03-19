import logging
from datetime import timedelta

from allauth.account.models import EmailAddress
from django.apps.registry import apps
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from openwisp_notifications.swapper import load_model, swapper_load_model

User = get_user_model()

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')
NotificationAppConfig = apps.get_app_config(Notification._meta.app_label)


OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')
Group = swapper_load_model('openwisp_users', 'Group')

start_time = timezone.now()
ten_minutes_ago = start_time - timedelta(minutes=10)
notification_queryset = Notification.objects.order_by('-timestamp')


class TestResendVerificationEmailView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.url = reverse('notifications:resend_verification_email')
        self.logger = logging.getLogger('openwisp_notifications.views')

    def test_unverified_primary_email_sends_email(self):
        email_address = EmailAddress.objects.get(user=self.user, primary=True)
        email_address.verified = False
        email_address.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('admin:index'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), f'Confirmation email sent to {self.user.email}.'
        )

    def test_auto_create_email_address(self):
        EmailAddress.objects.filter(user=self.user).delete()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        email_address = EmailAddress.objects.get(user=self.user)
        self.assertRedirects(response, reverse('admin:index'))
        self.assertTrue(email_address.primary)
        self.assertFalse(email_address.verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_last_non_primary_email_used(self):
        EmailAddress.objects.filter(user=self.user, primary=True).delete()
        EmailAddress.objects.create(
            user=self.user, email='alt1@example.com', primary=False, verified=False
        )
        last_email = EmailAddress.objects.create(
            user=self.user, email='alt2@example.com', primary=False, verified=False
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('admin:index'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [last_email.email])

    def test_redirect_with_next_param(self):
        safe_path = '/admin/safe-page/'
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'{self.url}?next={safe_path}')
        self.assertRedirects(response, safe_path, fetch_redirect_response=False)

    def test_log_unsafe_redirect_attempt(self):
        unsafe_url = 'http://evil.com/admin'
        self.client.login(username='testuser', password='testpass123')
        with self.assertLogs(logger=self.logger, level='WARNING') as log:
            response = self.client.get(f'{self.url}?next={unsafe_url}')
            self.assertRedirects(response, reverse('admin:index'))
        self.assertIn('Unsafe redirect attempted', log.output[0])

    def test_verified_email_shows_info(self):
        email_address = EmailAddress.objects.get(user=self.user, primary=True)
        email_address.verified = True
        email_address.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('admin:index'))
        self.assertEqual(len(mail.outbox), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your email is already verified.')

    def test_no_email_address_shows_message(self):
        EmailAddress.objects.filter(user=self.user).delete()
        self.user.email = ''
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('admin:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'No email address found for your account.')
