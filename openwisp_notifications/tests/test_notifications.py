from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_delete
from django.template import TemplateDoesNotExist
from django.test import TestCase
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.timesince import timesince
from openwisp_notifications import settings as app_settings
from openwisp_notifications.handlers import notify_handler
from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model
from openwisp_notifications.types import (
    NOTIFICATION_CHOICES,
    _unregister_notification_choice,
    get_notification_configuration,
    register_notification_type,
    unregister_notification_type,
)

from openwisp_users.models import Group, OrganizationUser
from openwisp_users.tests.utils import TestOrganizationMixin

User = get_user_model()

Notification = load_model('Notification')
notification_queryset = Notification.objects.order_by('-timestamp')
start_time = timezone.now()
ten_minutes_ago = start_time - timedelta(minutes=10)


class TestNotifications(TestOrganizationMixin, TestCase):
    app_label = 'openwisp_notifications'

    def setUp(self):
        self.admin = self._create_admin()
        self.notification_options = dict(
            sender=self.admin,
            recipient=self.admin,
            description='Test Notification',
            level='info',
            verb='Test Notification',
            email_subject='Test Email subject',
            url='https://localhost:8000/admin',
        )

    def _create_notification(self):
        return notify.send(**self.notification_options)

    def test_create_notification(self):
        operator = super()._create_operator()
        data = dict(
            email_subject='Test Email subject', url='https://localhost:8000/admin'
        )
        n = Notification.objects.create(
            actor=self.admin,
            recipient=self.admin,
            description='Test Notification Description',
            verb='Test Notification',
            action_object=operator,
            target=operator,
            data=data,
        )
        self.assertEqual(str(n), timesince(n.timestamp, timezone.now()))
        self.assertEqual(n.actor_object_id, self.admin.id)
        self.assertEqual(
            n.actor_content_type, ContentType.objects.get_for_model(self.admin)
        )
        self.assertEqual(n.action_object_object_id, operator.id)
        self.assertEqual(
            n.action_object_content_type, ContentType.objects.get_for_model(operator)
        )
        self.assertEqual(n.target_object_id, operator.id)
        self.assertEqual(
            n.target_content_type, ContentType.objects.get_for_model(operator)
        )
        self.assertEqual(n.verb, 'Test Notification')
        self.assertEqual(n.message, 'Test Notification Description')
        self.assertEqual(n.recipient, self.admin)

    def test_superuser_notifications_disabled(self):
        self.assertEqual(self.admin.notificationuser.email, True)
        self.admin.notificationuser.receive = False
        self.admin.notificationuser.save()
        self.assertEqual(self.admin.notificationuser.email, False)
        self._create_notification()
        n = notification_queryset.first()
        self.assertFalse(n.emailed)

    def test_email_sent(self):
        self._create_notification()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.admin.email])
        n = notification_queryset.first()
        self.assertEqual(mail.outbox[0].subject, n.data.get('email_subject'))
        self.assertIn(n.message, mail.outbox[0].body)
        self.assertIn(n.data.get('url'), mail.outbox[0].body)
        self.assertIn('https://', n.data.get('url'))

    def test_email_disabled(self):
        self.admin.notificationuser.email = False
        self.admin.notificationuser.save()
        self._create_notification()
        self.admin.email = ''
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_not_present(self):
        self.admin.email = ''
        self.admin.save()
        self._create_notification()
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_group_recipient(self):
        operator = self._get_operator()
        user = self._create_user(
            username='user', email='user@user.com', first_name='User', last_name='user'
        )
        op_group = Group.objects.get(name='Operator')
        op_group.user_set.add(operator)
        op_group.user_set.add(user)
        op_group.save()
        self.notification_options.update({'recipient': op_group})
        recipients = (operator, user)

        # Test for group with no target object
        n = self._create_notification().pop()
        if n[0] is notify_handler:
            notifications = n[1]
            self.assertEqual(len(notifications), 2)
            for notification, recipient in zip(notifications, recipients):
                self.assertEqual(notification.recipient, recipient)
        else:
            self.fail()

        # Test for group with target object of another organization
        org = self._get_org()
        target = self._create_user(
            username='target',
            email='target@target.com',
            first_name='Target',
            last_name='user',
        )
        OrganizationUser.objects.create(user=target, organization=org)
        target.organization_id = org.id
        self.notification_options.update({'target': target})
        self._create_notification()
        # No new notification should be created
        self.assertEqual(notification_queryset.count(), 2)

        # Test for group with target object of same organization
        # Adding operator to organization of target object
        OrganizationUser.objects.create(user=operator, organization=org)
        self._create_notification()
        self.assertEqual(notification_queryset.count(), 3)
        n = notification_queryset.first()
        self.assertEqual(n.recipient, operator)

    def test_queryset_recipient(self):
        super()._create_operator()
        users = User.objects.all()
        self.notification_options.update({'recipient': users})
        n = self._create_notification().pop()
        if n[0] is notify_handler:
            notifications = n[1]
            for notification, user in zip(notifications, users):
                self.assertEqual(notification.recipient, user)
        else:
            self.fail()

    def test_description_in_email_subject(self):
        self.notification_options.pop('email_subject')
        self._create_notification()
        n = notification_queryset.first()
        self.assertEqual(mail.outbox[0].subject, n.message[0:24])

    def test_handler_optional_tag(self):
        operator = self._create_operator()
        self.notification_options.update({'action_object': operator})
        self._create_notification()
        n = notification_queryset.first()
        self.assertEqual(
            n.action_object_content_type, ContentType.objects.get_for_model(operator)
        )
        self.assertEqual(n.action_object_object_id, str(operator.id))

    def test_organization_recipient(self):
        testorg = self._create_org()
        operator = self._create_operator()
        user = self._create_user(is_staff=False)
        OrganizationUser.objects.create(user=user, organization=testorg)
        OrganizationUser.objects.create(user=operator, organization=testorg)
        self.assertIsNotNone(operator.notificationuser)
        self.notification_options.pop('recipient')
        recipents = (self.admin, operator)
        operator.organization_id = testorg.id
        self.notification_options.update({'target': operator})
        n = self._create_notification().pop()
        if n[0] is notify_handler:
            notifications = n[1]
            for notification, recipient in zip(notifications, recipents):
                self.assertEqual(notification.recipient, recipient)
        else:
            self.fail()

    def test_no_organization(self):
        # Tests no target object is present
        self._create_org_user()
        user = self._create_user(
            username='user',
            email='user@user.com',
            first_name='User',
            last_name='user',
            is_staff=False,
        )
        self.notification_options.pop('recipient')
        self._create_notification()
        # Only superadmin should receive notification
        self.assertEqual(notification_queryset.count(), 1)
        n = notification_queryset.first()
        self.assertEqual(n.actor, self.admin)
        self.assertEqual(n.recipient, self.admin)

        # Tests no user from organization of target object
        org = self._create_org(name='test_org')
        OrganizationUser.objects.create(user=user, organization=org)
        self.notification_options.update({'target': user})
        self._create_notification()
        self.assertEqual(notification_queryset.count(), 2)
        # Only superadmin should receive notification
        n = notification_queryset.first()
        self.assertEqual(n.actor, self.admin)
        self.assertEqual(n.recipient, self.admin)
        self.assertEqual(n.target, user)

    def test_default_notification_type(self):
        self.notification_options.pop('verb')
        self.notification_options.update({'type': 'default'})
        self._create_notification()
        n = notification_queryset.first()
        self.assertEqual(n.level, 'info')
        self.assertEqual(n.verb, 'default verb')
        self.assertIn(
            'Default notification with default verb and level info by', n.message
        )
        self.assertEqual(n.email_subject, '[example.com] Default Notification Subject')

    def test_misc_notification_type_validation(self):
        with self.subTest('Registering with incomplete notification configuration.'):
            with self.assertRaises(AssertionError):
                register_notification_type('test_type', dict())

        with self.subTest('Registering with improper notification type name'):
            with self.assertRaises(ImproperlyConfigured):
                register_notification_type(['test_type'], dict())

        with self.subTest('Registering with improper notification configuration'):
            with self.assertRaises(ImproperlyConfigured):
                register_notification_type('test_type', tuple())

        with self.subTest('Unregistering with improper notification type name'):
            with self.assertRaises(ImproperlyConfigured):
                unregister_notification_type(dict())

    def test_notification_type_message_template(self):
        message_template = {
            'level': 'info',
            'verb': 'message template verb',
            'name': 'Message Template Type',
            'email_subject': '[{site.name}] Messsage Template Subject',
        }

        with self.subTest('Register type with non existent message template'):
            with self.assertRaises(TemplateDoesNotExist):
                message_template.update({'message_template': 'wrong/path.md'})
                register_notification_type('message_template', message_template)

        with self.subTest('Registering type with message template'):
            message_template.update(
                {'message_template': 'openwisp_notifications/default_message.md'}
            )
            register_notification_type('message_template', message_template)
            self.notification_options.update({'type': 'message_template'})
            self._create_notification()
            n = notification_queryset.first()
            self.assertEqual(n.type, 'message_template')
            self.assertEqual(n.email_subject, '[example.com] Messsage Template Subject')

        with self.subTest('Links in notification message'):
            exp_message = (
                '<p>info : None message template verb </p>\n'
                f'<p><a href="http://example.com/admin/openwisp_users/user/{self.admin.id}/change/">admin</a>'
                '\nreports\n<a href="#">None</a>\nmessage template verb.</p>'
            )
            self.assertEqual(n.message, exp_message)

    def test_register_unregister_notification_type(self):
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'test',
            'verb': 'testing',
            'message': '{notification.verb} initiated by {notification.actor} since {notification}',
            'email_subject': '[{site.name}] {notification.verb} reported by {notification.actor}',
        }

        with self.subTest('Registering new notification type'):
            register_notification_type('test_type', test_type)
            self.notification_options.update({'type': 'test_type'})
            self._create_notification()
            n = notification_queryset.first()
            self.assertEqual(n.level, 'test')
            self.assertEqual(n.verb, 'testing')
            self.assertEqual(
                n.message, '<p>testing initiated by admin since 0\xa0minutes</p>',
            )
            self.assertEqual(n.email_subject, '[example.com] testing reported by admin')

        with self.subTest('Re-registering a notification type'):
            with self.assertRaises(ImproperlyConfigured):
                register_notification_type('test_type', test_type)

        with self.subTest('Check registration in NOTIFICATION_CHOICES'):
            notification_choice = NOTIFICATION_CHOICES[-1]
            self.assertTupleEqual(
                notification_choice, ('test_type', 'Test Notification Type')
            )

        with self.subTest('Unregistering a notification type which does not exists'):
            with self.assertRaises(ImproperlyConfigured):
                unregister_notification_type('wrong type')

        with self.subTest('Unregistering a notification choice which does not exists'):
            with self.assertRaises(ImproperlyConfigured):
                _unregister_notification_choice('wrong type')

        with self.subTest('Unregistering "test_type"'):
            unregister_notification_type('test_type')
            with self.assertRaises(ImproperlyConfigured):
                get_notification_configuration('test_type')

        with self.subTest('Using non existing notification type for new notification'):
            with self.assertRaises(ImproperlyConfigured):
                self._create_notification()
                n = notification_queryset.first()

        with self.subTest('Check unregistration in NOTIFICATION_CHOICES'):
            with self.assertRaises(ImproperlyConfigured):
                _unregister_notification_choice('test_type')

    def test_notification_type_email(self):
        operator = self._create_operator()
        exp_target_url = (
            f'http://example.com/admin/openwisp_users/user/{operator.id}/change/'
        )
        exp_email_body = '{message}\n\nFor more information see {target_url}.'
        self.notification_options.update({'type': 'default'})

        with self.subTest('Test email with URL option'):
            url = self.notification_options['url']
            self._create_notification()
            email = mail.outbox.pop()
            n = notification_queryset.first()
            self.assertEqual(
                email.body,
                exp_email_body.format(
                    message=strip_tags(n.message),
                    target_url=self.notification_options['url'],
                ),
            )
            html_message, content_type = email.alternatives.pop()
            self.assertEqual(content_type, 'text/html')
            self.assertIn(n.message, html_message)
            self.assertIn(
                f'For further information see <a href="{url}">{url}</a>.', html_message,
            )

        with self.subTest('Test email without URL option and target object'):
            self.notification_options.pop('url')
            self._create_notification()
            email = mail.outbox.pop()
            n = notification_queryset.first()
            self.assertEqual(email.body, strip_tags(n.message))
            html_message, content_type = email.alternatives.pop()
            self.assertEqual(content_type, 'text/html')
            self.assertIn(n.message, html_message)
            self.assertNotIn(
                f'<a href="{exp_target_url}">', html_message,
            )

        with self.subTest('Test email with target object'):
            self.notification_options.update({'target': operator})
            self._create_notification()
            email = mail.outbox.pop()
            n = notification_queryset.first()
            html_message, content_type = email.alternatives.pop()
            self.assertEqual(
                email.body,
                exp_email_body.format(
                    message=strip_tags(n.message), target_url=exp_target_url
                ),
            )
            self.assertEqual(
                email.subject, '[example.com] Default Notification Subject'
            )
            self.assertEqual(content_type, 'text/html')
            self.assertIn(
                f'<img src="{app_settings.OPENWISP_NOTIFICATIONS_EMAIL_LOGO}"'
                ' alt="Logo" id="logo" class="logo">',
                html_message,
            )
            self.assertIn(n.message, html_message)
            self.assertIn(
                f'<a href="{exp_target_url}">For further information see'
                f' "{n.target_content_type.model}: {n.target}".</a>',
                html_message,
            )

    def test_responsive_html_email(self):
        self.notification_options.update({'type': 'default'})
        self._create_notification()
        email = mail.outbox.pop()
        html_message, content_type = email.alternatives.pop()
        self.assertIn('@media screen and (max-width: 250px)', html_message)
        self.assertIn('@media screen and (max-width: 600px)', html_message)
        self.assertIn('@media screen and (min-width: 600px)', html_message)
        self.assertIn('<tr class="m-notification-header">', html_message)

    def test_missing_relation_object(self):
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': (
                '{notification.verb} initiated by'
                '[{notification.actor}]({notification.actor_link}) with'
                ' [{notification.action_object}]({notification.action_link}) for'
                ' [{notification.target}]({notification.target_link}).'
            ),
            'email_subject': (
                '[{site.name}] {notification.verb} reported by'
                ' {notification.actor} with {notification.action_object} for {notification.target}'
            ),
        }
        register_notification_type('test_type', test_type)
        self.notification_options.pop('email_subject')
        self.notification_options.update({'type': 'test_type'})
        operator = self._get_operator()

        with self.subTest("Missing target object after creation"):
            self.notification_options.update({'target': operator})
            self._create_notification()
            pre_delete.send(sender=self, instance=operator)

            n_count = notification_queryset.count()
            self.assertEqual(n_count, 0)

        with self.subTest("Missing action object after creation"):
            self.notification_options.pop('target')
            self.notification_options.update({'action_object': operator})
            self._create_notification()
            pre_delete.send(sender=self, instance=operator)

            n_count = notification_queryset.count()
            self.assertEqual(n_count, 0)

        with self.subTest("Missing actor object after creation"):
            self.notification_options.pop('action_object')
            self.notification_options.pop('url')
            self.notification_options.update({'sender': operator})
            self._create_notification()
            pre_delete.send(sender=self, instance=operator)

            n_count = notification_queryset.count()
            self.assertEqual(n_count, 0)

        unregister_notification_type('test_type')

    def test_notification_invalid_message_attribute(self):
        self.notification_options.update({'type': 'test_type'})
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': '{notification.actor.random}',
            'email_subject': '[{site.name}] {notification.actor.random}',
        }
        register_notification_type('test_type', test_type)
        self._create_notification()
        self.assertIsNone(notification_queryset.first())
        unregister_notification_type('test_type')

    @patch.object(app_settings, 'OPENWISP_NOTIFICATIONS_HTML_EMAIL', False)
    def test_no_html_email(self, *args):
        operator = self._create_operator()
        self.notification_options.update(
            {'type': 'default', 'target': operator, 'url': None}
        )
        self._create_notification()
        email = mail.outbox.pop()
        n = notification_queryset.first()
        self.assertEqual(
            email.body,
            f'{strip_tags(n.message)}\n\nFor more information see'
            f' http://example.com/admin/openwisp_users/user/{operator.id}/change/.',
        )
        self.assertEqual(email.subject, '[example.com] Default Notification Subject')
        self.assertFalse(email.alternatives)

    def test_related_objects_database_query(self):
        operator = self._get_operator()
        self.notification_options.update(
            {'action_object': operator, 'target': operator}
        )
        self._create_notification()
        with self.assertNumQueries(2):
            # 2 queries since admin is already chached
            n = notification_queryset.first()
            self.assertEqual(n.actor, self.admin)
            self.assertEqual(n.action_object, operator)
            self.assertEqual(n.target, operator)

    @patch.object(app_settings, 'OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT', 0)
    def test_notification_cache_timeout(self):
        # Timeout=0 means value is not cached
        operator = self._get_operator()
        self.notification_options.update(
            {'action_object': operator, 'target': operator}
        )
        self._create_notification()

        n = notification_queryset.first()
        with self.assertNumQueries(3):
            # Expect database query for each operation, nothing is cached
            self.assertEqual(n.actor, self.admin)
            self.assertEqual(n.action_object, operator)
            self.assertEqual(n.target, operator)

        # Test cache is not set
        self.assertIsNone(cache.get(Notification._cache_key(self.admin.pk)))
        self.assertIsNone(cache.get(Notification._cache_key(operator.pk)))
