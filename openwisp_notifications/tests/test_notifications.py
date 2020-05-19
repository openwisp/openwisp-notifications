from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from django.utils.timesince import timesince
from openwisp_notifications.handlers import notify_handler
from openwisp_notifications.signals import notify
from swapper import load_model

from openwisp_users.models import Group, OrganizationUser
from openwisp_users.tests.utils import TestOrganizationMixin

User = get_user_model()

Notification = load_model('openwisp_notifications', 'Notification')
notification_queryset = Notification.objects.order_by('-timestamp')
start_time = timezone.now()
ten_minutes_ago = start_time - timedelta(minutes=10)


class TestNotifications(TestOrganizationMixin, TestCase):
    def setUp(self):
        self.admin = self._create_admin()
        self.notification_options = dict(
            sender=self.admin,
            recipient=self.admin,
            description="Test Notification",
            verb="Test Notification",
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
        self.assertEqual(n.description, 'Test Notification Description')
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
        self.assertIn(n.description, mail.outbox[0].body)
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
        self.assertEqual(mail.outbox[0].subject, n.description[0:24])

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
