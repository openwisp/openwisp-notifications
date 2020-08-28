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
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.timesince import timesince

from openwisp_notifications import settings as app_settings
from openwisp_notifications import tasks
from openwisp_notifications.handlers import notify_handler
from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.tests.test_helpers import (
    register_notification_type,
    unregister_notification_type,
)
from openwisp_notifications.types import (
    NOTIFICATION_CHOICES,
    _unregister_notification_choice,
    get_notification_configuration,
)
from openwisp_notifications.utils import _get_absolute_url
from openwisp_users.tests.utils import TestOrganizationMixin

User = get_user_model()

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')

OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')
Group = swapper_load_model('openwisp_users', 'Group')

start_time = timezone.now()
ten_minutes_ago = start_time - timedelta(minutes=10)
notification_queryset = Notification.objects.order_by('-timestamp')


class TestNotifications(TestOrganizationMixin, TestCase):
    def setUp(self):
        self.admin = self._create_admin()
        self.notification_options = dict(
            sender=self.admin,
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

    def test_create_with_extra_data(self):
        register_notification_type(
            'error_type',
            {
                'verbose_name': 'Error',
                'level': 'error',
                'verb': 'error',
                'message': 'Error: {error}',
                'email_subject': 'Error subject: {error}',
            },
        )
        error = '500 Internal Server Error'
        notify.send(
            type='error_type',
            url='https://localhost:8000/admin',
            recipient=self.admin,
            sender=self.admin,
            error=error,
        )
        self.assertEqual(notification_queryset.count(), 1)
        n = notification_queryset.first()
        self.assertIn(f'Error: {error}', n.message)
        self.assertEqual(n.email_subject, f'Error subject: {error}')

    def test_superuser_notifications_disabled(self):
        target_obj = self._get_org_user()
        self.notification_options.update({'type': 'default', 'target': target_obj})
        notification_preference = NotificationSetting.objects.get(
            user_id=self.admin.pk,
            organization_id=target_obj.organization.pk,
            type='default',
        )
        self.assertEqual(notification_preference.email, None)
        notification_preference.web = False
        notification_preference.save()
        notification_preference.refresh_from_db()
        self.assertEqual(notification_preference.email, False)
        self._create_notification()
        self.assertEqual(notification_queryset.count(), 0)

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
        self.notification_options.update(
            {'type': 'default', 'target': self._get_org_user()}
        )
        NotificationSetting.objects.filter(
            user_id=self.admin.pk, type='default'
        ).update(email=False)
        self._create_notification()
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_not_present(self):
        self.admin.email = ''
        self.admin.save()
        self._create_notification()
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_group_recipient(self):
        org = self._get_org()
        operator = self._get_operator()
        user = self._create_user(
            username='user', email='user@user.com', first_name='User', last_name='user'
        )
        op_group = Group.objects.get(name='Operator')
        op_group.user_set.add(operator)
        op_group.user_set.add(user)
        op_group.save()
        self.notification_options.update({'recipient': op_group, 'type': 'default'})
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
        self._create_org_user(user=target, organization=org)
        target.organization_id = org.id
        self.notification_options.update({'target': target})
        self._create_notification()
        # No new notification should be created
        self.assertEqual(notification_queryset.count(), 2)

        # Test for group with target object of same organization
        # Adding operator to organization of target object
        self._create_org_user(user=operator, organization=org, is_admin=True)
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
        self.notification_options.update({'type': 'default'})
        testorg = self._create_org()
        operator = self._create_operator()
        user = self._create_user(is_staff=False)
        OrganizationUser.objects.create(user=user, organization=testorg)
        OrganizationUser.objects.create(user=operator, organization=testorg)
        recipients = (self.admin, operator)
        operator.organization_id = testorg.id
        self.notification_options.update({'target': operator})
        n = self._create_notification().pop()
        if n[0] is notify_handler:
            notifications = n[1]
            for notification, recipient in zip(notifications, recipients):
                self.assertEqual(notification.recipient, recipient)
        else:
            self.fail()

    def test_no_organization(self):
        # Tests no target object is present
        self.notification_options.update({'type': 'default'})
        self._create_org_user()
        user = self._create_user(
            username='user',
            email='user@user.com',
            first_name='User',
            last_name='user',
            is_staff=False,
        )
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
            'verbose_name': 'Message Template Type',
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
            url = _get_absolute_url(
                reverse('admin:openwisp_users_user_change', args=(self.admin.pk,))
            )
            message = (
                '<p>info : None message template verb </p>\n'
                f'<p><a href="{url}">admin</a>'
                '\nreports\n<a href="#">None</a>\nmessage template verb.</p>'
            )
            self.assertEqual(n.message, message)

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
        email_body = '{message}\n\nFor more information see {target_url}.'
        self.notification_options.update({'type': 'default'})

        with self.subTest('Test email with URL option'):
            url = self.notification_options['url']
            self._create_notification()
            email = mail.outbox.pop()
            n = notification_queryset.first()
            self.assertEqual(
                email.body,
                email_body.format(
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
                f'<a href="{n.redirect_view_url}">', html_message,
            )

        with self.subTest('Test email with target object'):
            self.notification_options.update({'target': operator})
            self._create_notification()
            email = mail.outbox.pop()
            n = notification_queryset.first()
            html_message, content_type = email.alternatives.pop()
            self.assertEqual(
                email.body,
                email_body.format(
                    message=strip_tags(n.message), target_url=n.redirect_view_url
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
                f'<a href="{n.redirect_view_url}">For further information see'
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
            f'{strip_tags(n.message)}\n\nFor more information see {n.redirect_view_url}.',
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
            # 2 queries since admin is already cached
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

    def test_notification_target_content_type_deleted(self):
        operator = self._get_operator()
        self.notification_options.update(
            {'action_object': operator, 'target': operator, 'type': 'default'}
        )
        self._create_notification()
        ContentType.objects.get_for_model(operator._meta.model).delete()
        ContentType.objects.clear_cache()
        # DoesNotExists exception should not be raised.
        operator.delete()

    def test_delete_old_notification(self):
        days_old = 91
        # Create notification with current timestamp
        self.notification_options.update({'type': 'default'})
        self._create_notification()
        # Create notification with older timestamp
        self.notification_options.update(
            {'timestamp': timezone.now() - timedelta(days=days_old)}
        )
        self._create_notification()

        self.assertEqual(notification_queryset.count(), 2)
        tasks.delete_old_notifications.delay(days_old)
        self.assertEqual(notification_queryset.count(), 1)

    def test_unregistered_notification_type_related_notification(self):
        # Notifications related to notification type should
        # get deleted on unregistration of notification type
        default_type_config = get_notification_configuration('default')
        self.notification_options.update({'type': 'default'})
        unregister_notification_type('default')
        self.assertEqual(notification_queryset.count(), 0)

        register_notification_type('default', default_type_config)

    def test_notification_type_email_notification_setting_true(self):
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': 'Test message',
            'email_subject': 'Test Email Subject',
            'email_notification': True,
        }

        register_notification_type('test_type', test_type)
        target_obj = self._get_org_user()
        self.notification_options.update({'type': 'test_type', 'target': target_obj})

        with self.subTest('Test user email preference not defined'):
            self._create_notification()
            self.assertEqual(len(mail.outbox), 1)
            self.assertIsNotNone(mail.outbox.pop())

        with self.subTest('Test user email preference is "False"'):
            NotificationSetting.objects.filter(
                user=self.admin, type='test_type',
            ).update(email=False)
            self._create_notification()
            self.assertEqual(len(mail.outbox), 0)

        unregister_notification_type('test_type')

    def test_notification_type_email_notification_setting_false(self):
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': 'Test message',
            'email_subject': 'Test Email Subject',
            'email_notification': False,
        }

        register_notification_type('test_type', test_type)
        target_obj = self._get_org_user()
        self.notification_options.update({'type': 'test_type', 'target': target_obj})

        with self.subTest('Test user email preference not defined'):
            self._create_notification()
            self.assertEqual(len(mail.outbox), 0)

        with self.subTest('Test user email preference is "True"'):
            NotificationSetting.objects.filter(
                user=self.admin, type='test_type',
            ).update(email=True)
            self._create_notification()
            self.assertEqual(len(mail.outbox), 1)

        unregister_notification_type('test_type')

    def test_notification_type_web_notification_setting_true(self):
        self.notification_options.update({'target': self._get_org_user()})
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': 'Test message',
            'email_subject': 'Test Email Subject',
            'web_notification': True,
        }

        register_notification_type('test_type', test_type)
        self.notification_options.update({'type': 'test_type'})

        with self.subTest('Test user web preference not defined'):
            self._create_notification()
            self.assertEqual(notification_queryset.delete()[0], 1)

        with self.subTest('Test user web preference is "False"'):
            NotificationSetting.objects.filter(
                user=self.admin, type='test_type'
            ).update(web=False)
            self._create_notification()
            self.assertEqual(notification_queryset.count(), 0)

        unregister_notification_type('test_type')

    def test_notification_type_web_notification_setting_false(self):
        target_obj = self._get_org_user()
        self.notification_options.update({'target': target_obj})
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': 'Test message',
            'email_subject': 'Test Email Subject',
            'web_notification': False,
        }

        register_notification_type('test_type', test_type)
        self.notification_options.update({'type': 'test_type'})

        with self.subTest('Test user web preference not defined'):
            self._create_notification()
            self.assertEqual(notification_queryset.count(), 0)

        with self.subTest('Test user email preference is "True"'):
            notification_setting = NotificationSetting.objects.get(
                user=self.admin, type='test_type', organization=target_obj.organization
            )
            notification_setting.email = True
            notification_setting.save()
            notification_setting.refresh_from_db()
            self.assertFalse(notification_setting.email)

        with self.subTest('Test user web preference is "True"'):
            NotificationSetting.objects.filter(
                user=self.admin, type='test_type'
            ).update(web=True)
            self._create_notification()
            self.assertEqual(notification_queryset.count(), 1)

        unregister_notification_type('test_type')

    def test_notification_type_email_web_notification_defaults(self):
        test_type = {
            'verbose_name': 'Test Notification Type',
            'level': 'info',
            'verb': 'testing',
            'message': 'Test message',
            'email_subject': 'Test Email Subject',
        }
        register_notification_type('test_type', test_type)

        notification_type_config = get_notification_configuration('test_type')
        self.assertTrue(notification_type_config['web_notification'])
        self.assertTrue(notification_type_config['email_notification'])

        unregister_notification_type('test_type')

    def test_inactive_user_not_receive_notification(self):
        target = self._get_org_user()
        self.notification_options.update({'target': target})

        with self.subTest('Test superuser is inactive'):
            self.admin.is_active = False
            self.admin.save()

            self._create_notification()
            self.assertEqual(notification_queryset.count(), 0)

        # Create org admin
        org_admin = self._create_org_user(user=self._get_operator(), is_admin=True)

        with self.subTest('Test superuser is inactive but org admin is active'):
            self._create_notification()
            self.assertEqual(notification_queryset.count(), 1)
            notification = notification_queryset.first()
            self.assertEqual(notification.recipient, org_admin.user)

        # Cleanup
        notification_queryset.delete()

        with self.subTest('Test both superuser and org admin is inactive'):
            org_admin.user.is_active = False
            org_admin.user.save()

            self._create_notification()
            self.assertEqual(notification_queryset.count(), 0)

        with self.subTest('Test superuser is active and org admin is inactive'):
            self.admin.is_active = True
            self.admin.save()

            self._create_notification()
            self.assertEqual(notification_queryset.count(), 1)
            notification = notification_queryset.first()
            self.assertEqual(notification.recipient, self.admin)

    def test_notification_received_only_by_org_admin(self):
        self.admin.delete()
        org_object = self._get_org_user()
        self.notification_options.update({'sender': org_object, 'target': org_object})
        self._create_org_user(
            user=self._create_user(username='user', email='user@user.com')
        )
        org_admin = self._create_org_user(user=self._get_operator(), is_admin=True)

        self._create_notification()
        self.assertEqual(notification_queryset.count(), 1)
        notification = notification_queryset.first()
        self.assertEqual(notification.recipient, org_admin.user)
