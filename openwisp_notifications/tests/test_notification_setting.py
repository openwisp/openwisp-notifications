from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.test import TransactionTestCase

from openwisp_notifications.handlers import (
    notification_type_registered_unregistered_handler,
)
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.tasks import (
    create_superuser_notification_settings,
    superuser_demoted_notification_setting,
)
from openwisp_notifications.tests.test_helpers import (
    base_register_notification_type,
    base_unregister_notification_type,
    mock_notification_types,
    register_notification_type,
    test_notification_type,
)
from openwisp_users.tests.utils import TestOrganizationMixin

NotificationSetting = load_model("NotificationSetting")
Organization = swapper_load_model("openwisp_users", "Organization")
OrganizationUser = swapper_load_model("openwisp_users", "OrganizationUser")

ns_queryset = NotificationSetting.objects.filter(type="default")


class TestNotificationSetting(TestOrganizationMixin, TransactionTestCase):
    def setUp(self):
        self.default_org = self._get_org("default")

    def _create_staff_org_admin(self):
        return self._create_org_user(user=self._create_operator(), is_admin=True)

    def test_no_user(self):
        self.assertEqual(ns_queryset.count(), 0)

    def test_superuser_created(self):
        admin = self._get_admin()
        self.assertEqual(ns_queryset.filter(user=admin).count(), 1)

    def test_user_created(self):
        self._get_user()
        self.assertEqual(ns_queryset.count(), 0)

    @mock_notification_types
    def test_notification_type_registered(self):
        register_notification_type("test", test_notification_type)
        queryset = NotificationSetting.objects.filter(type="test")

        self._get_user()
        self.assertEqual(queryset.count(), 0)

        self._get_admin()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().__str__(), "Test Notification Type - default")

    def test_organization_created_no_initial_user(self):
        org = self._get_org()
        queryset = ns_queryset.filter(organization=org)
        self.assertEqual(ns_queryset.count(), 0)

        # Notification setting is not created for normal user
        self._get_user()
        self.assertEqual(queryset.count(), 0)

        self._get_admin()
        self.assertEqual(queryset.count(), 1)

    def test_organization_user(self):
        karen = self._get_user()
        ken = self._create_user(username="ken", email="ken@ken.com")
        org = self._get_org()
        OrganizationUser.objects.create(user=karen, organization=org, is_admin=True)
        org_user = OrganizationUser.objects.create(
            user=ken, organization=org, is_admin=True
        )
        self.assertEqual(ns_queryset.count(), 2)
        org_user.delete()
        # OrganizationOwner can not be deleted before transferring ownership
        self.assertEqual(ns_queryset.filter(deleted=False).count(), 1)
        self.assertEqual(ns_queryset.filter(deleted=True).count(), 1)

    @mock_notification_types
    def test_register_notification_org_user(self):
        self._create_staff_org_admin()

        queryset = NotificationSetting.objects.filter(type="test")
        self.assertEqual(queryset.count(), 0)
        register_notification_type("test", test_notification_type)
        self.assertEqual(queryset.count(), 1)

    @mock_notification_types
    def test_post_migration_handler(self):
        """
        Tests notification_type_registered_unregistered_handler for:
        1. Soft-deleting NotificationSettings when notification types are unregistered
        2. Auto-creating NotificationSettings for newly registered notification types
        3. Preserving existing user preferences during handler execution
        """
        from openwisp_notifications.types import NOTIFICATION_CHOICES

        # Simulates loading of app when Django server starts
        admin = self._get_admin()
        org_user = self._create_staff_org_admin()
        register_notification_type("test_unmodified", test_notification_type)
        self.assertEqual(ns_queryset.count(), 3)
        # Disable notifications to test preservation of user preferences
        NotificationSetting.objects.filter(
            type__in=["test_unmodified", "default"], user=admin
        ).update(email=False, web=False)

        base_unregister_notification_type("default")
        base_register_notification_type("test", test_notification_type)

        # Delete existing global notification settings
        NotificationSetting.objects.filter(
            user=org_user.user, type=None, organization=None
        ).delete()

        NotificationSetting.objects.filter(
            user=admin, type=None, organization=None
        ).delete()

        notification_type_registered_unregistered_handler(sender=self)

        # Notification Setting for "default" type are deleted
        self.assertEqual(ns_queryset.filter(type="default", deleted=True).count(), 3)

        # Notification Settings for "test" type are created
        # We exclude the global row (type=None) to correctly count only typed settings
        queryset = NotificationSetting.objects.filter(deleted=False).exclude(type=None)
        notification_types_count = len(NOTIFICATION_CHOICES)
        self.assertEqual(queryset.count(), 3 * notification_types_count)
        self.assertEqual(
            queryset.filter(user=admin).count(), 2 * notification_types_count
        )
        self.assertEqual(
            queryset.filter(user=org_user.user).count(), 1 * notification_types_count
        )

        # Check Global Notification Setting is created and not deleted
        self.assertEqual(
            NotificationSetting.objects.filter(
                user=admin, type=None, organization=None, deleted=False
            ).count(),
            1,
        )
        self.assertEqual(
            NotificationSetting.objects.filter(
                user=org_user.user, type=None, organization=None, deleted=False
            ).count(),
            1,
        )
        # "test_unmodified" notifications should be disabled
        self.assertEqual(
            NotificationSetting.objects.filter(
                user=admin,
                type="test_unmodified",
                web=False,
                email=False,
                deleted=False,
            ).count(),
            2,
        )
        self.assertEqual(
            NotificationSetting.objects.filter(
                user=admin, type="default", web=False, email=False, deleted=True
            ).count(),
            2,
        )

    def test_superuser_demoted_to_user(self):
        admin = self._get_admin()
        admin.is_superuser = False
        admin.save()

        self.assertEqual(ns_queryset.filter(deleted=True).count(), 1)

    def test_user_promoted_to_superuser(self):
        user = self._create_operator()
        self.assertEqual(ns_queryset.count(), 0)

        user.is_superuser = True
        user.save()

        self.assertEqual(ns_queryset.count(), 1)

    def test_superuser_demoted_to_org_admin(self):
        admin = self._get_admin()
        admin.is_superuser = False
        admin.save()
        org = Organization.objects.get(name="default")
        OrganizationUser.objects.create(user=admin, organization=org, is_admin=True)

        self.assertEqual(ns_queryset.count(), 1)

    def test_org_admin_demoted_to_org_user(self):
        org_user = self._create_staff_org_admin()
        self.assertEqual(ns_queryset.count(), 1)
        org_user.organizationowner.delete()
        org_user.is_admin = False
        org_user.full_clean()
        org_user.save()
        self.assertEqual(ns_queryset.filter(deleted=False).count(), 0)
        self.assertEqual(ns_queryset.filter(deleted=True).count(), 1)

    def test_org_user_promoted_to_org_admin(self):
        org_user = self._create_org_user(user=self._create_operator(), is_admin=False)
        self.assertEqual(ns_queryset.count(), 0)
        org_user.is_admin = True
        org_user.full_clean()
        org_user.save()
        self.assertEqual(ns_queryset.count(), 1)

    def test_multiple_org_membership(self):
        user = self._get_user()
        default_org = Organization.objects.first()
        test_org = self._get_org()
        self.assertEqual(ns_queryset.count(), 0)

        OrganizationUser.objects.create(
            user=user, organization=default_org, is_admin=True
        )
        self.assertEqual(ns_queryset.count(), 1)

        OrganizationUser.objects.create(user=user, organization=test_org, is_admin=True)
        self.assertEqual(ns_queryset.count(), 2)

    @mock_notification_types
    def test_notification_setting_full_clean(self):
        test_type = {
            "verbose_name": "Test Notification Type",
            "level": "info",
            "verb": "testing",
            "message": "Test message",
            "email_subject": "Test Email Subject",
            "web_notification": False,
            "email_notification": False,
        }
        register_notification_type("test_type", test_type)
        self._get_admin()
        queryset = NotificationSetting.objects.filter(type="test_type")
        queryset.update(email=False, web=False)
        notification_setting = queryset.first()

        notification_setting.full_clean()
        notification_setting.save()
        self.assertIsNone(notification_setting.email)
        self.assertIsNone(notification_setting.web)

    def test_organization_user_updated(self):
        default_org = Organization.objects.first()
        org_user = self._create_staff_org_admin()
        self.assertNotEqual(org_user.organization_id, default_org.pk)
        self.assertEqual(ns_queryset.count(), 1)
        org_user.organization_id = default_org.pk
        org_user.full_clean()
        org_user.save()

        self.assertEqual(ns_queryset.filter(deleted=True).count(), 1)
        self.assertEqual(ns_queryset.filter(deleted=False).count(), 1)
        notification_setting = ns_queryset.first()
        self.assertEqual(notification_setting.organization.pk, default_org.pk)

    def test_organization_user_no_change_save(self):
        org_user = self._create_staff_org_admin()
        ns = ns_queryset.first()
        self.assertEqual(ns_queryset.count(), 1)
        org_user.full_clean()
        org_user.save()
        self.assertEqual(ns_queryset.count(), 1)
        update_ns = ns_queryset.first()
        self.assertEqual(ns.id, update_ns.id)

    def test_org_user_promoted_to_org_admin_with_org_change(self):
        default_org = Organization.objects.get(slug="default")
        org_user = self._create_org_user(user=self._create_operator(), is_admin=False)
        self.assertEqual(ns_queryset.count(), 0)
        org_user.is_admin = True
        org_user.organization = default_org
        org_user.full_clean()
        org_user.save()
        self.assertEqual(ns_queryset.count(), 1)
        ns = ns_queryset.first()
        self.assertEqual(ns.organization, default_org)
        self.assertEqual(ns.user, org_user.user)

    def test_deleted_notificationsetting_autocreated(self):
        org_user = self._create_staff_org_admin()
        self.assertEqual(ns_queryset.count(), 1)
        ns = ns_queryset.first()
        ns.deleted = True
        ns.full_clean()
        ns.save()

        # Emit post_save for organization user
        post_save.send(sender=OrganizationUser, instance=org_user, created=False)

        self.assertEqual(ns_queryset.count(), 1)
        ns.refresh_from_db()
        self.assertEqual(ns.deleted, False)

    @patch.object(superuser_demoted_notification_setting, "delay")
    @patch.object(create_superuser_notification_settings, "delay")
    def test_task_not_called_on_user_login(self, created_mock, demoted_mock):
        admin = self._create_admin()
        # Called once for the superuser
        self.assertEqual(created_mock.call_count, 1)
        org_user = self._create_staff_org_admin()
        # Called once again for the staff org admin user
        self.assertEqual(created_mock.call_count, 2)
        created_mock.reset_mock()
        with self.subTest("Test task not called if superuser status is unchanged"):
            admin.username = "new_admin"
            admin.save()
            created_mock.assert_not_called()
            demoted_mock.assert_not_called()
        with self.subTest("Test task not called when superuser logs in"):
            self.client.force_login(admin)
            created_mock.assert_not_called()
            demoted_mock.assert_not_called()
        with self.subTest("Test task not called when org user logs in"):
            self.client.force_login(org_user.user)
            created_mock.assert_not_called()
            demoted_mock.assert_not_called()
        with self.subTest("Test task called when superuser status changed"):
            admin.is_superuser = False
            admin.save()
            demoted_mock.assert_called_once()
            created_mock.assert_not_called()
            admin.is_superuser = True
            admin.save()
            created_mock.assert_called_once()

    @patch.object(superuser_demoted_notification_setting, "delay")
    @patch.object(create_superuser_notification_settings, "delay")
    def test_privilege_flags_do_not_leak_to_unrelated_saves(
        self, created_mock, demoted_mock
    ):
        with self.subTest("gained privileges"):
            user = self._create_user(
                username="gain_privilege", email="gain_privilege@example.com"
            )
            user.is_staff = True
            user.save()
            created_mock.assert_called_once()
            demoted_mock.assert_not_called()
            created_mock.reset_mock()
            user.username = "gain_privilege_updated"
            user.save(update_fields=["username"])
            created_mock.assert_not_called()
            demoted_mock.assert_not_called()
        created_mock.reset_mock()
        demoted_mock.reset_mock()
        with self.subTest("lost privileges"):
            user = self._create_user(
                username="lose_privilege",
                email="lose_privilege@example.com",
                is_staff=True,
            )
            created_mock.reset_mock()
            user.is_staff = False
            user.save()
            demoted_mock.assert_called_once()
            created_mock.assert_not_called()
            demoted_mock.reset_mock()
            user.username = "lose_privilege_updated"
            user.save(update_fields=["username"])
            created_mock.assert_not_called()
            demoted_mock.assert_not_called()

    def test_global_notification_setting_update(self):
        admin = self._get_admin()
        org = self._get_org("default")
        global_setting = NotificationSetting.objects.get(
            user=admin, type=None, organization=None
        )

        # Update global settings
        global_setting.email = False
        global_setting.web = False
        global_setting.full_clean()
        global_setting.save()

        with self.subTest(
            "Test global web to False while ensuring at least one email setting is True"
        ):
            # Set the default type notification setting's email to True
            NotificationSetting.objects.filter(
                user=admin, organization=org, type="default"
            ).update(email=True)

            global_setting.web = True
            global_setting.full_clean()
            global_setting.save()

            self.assertTrue(
                NotificationSetting.objects.filter(
                    user=admin, organization=org, email=True, type="default"
                ).exists()
            )

        with self.subTest("Test global web to False"):
            global_setting.web = False
            global_setting.full_clean()
            global_setting.save()

            self.assertFalse(
                NotificationSetting.objects.filter(
                    user=admin, organization=org, web=True
                ).exists()
            )
            self.assertFalse(
                NotificationSetting.objects.filter(
                    user=admin, organization=org, email=True
                ).exists()
            )

    def test_global_notification_setting_delete(self):
        admin = self._get_admin()
        global_setting = NotificationSetting.objects.get(
            user=admin, type=None, organization=None
        )
        self.assertEqual(str(global_setting), "Global Setting")
        global_setting.delete()
        self.assertEqual(
            NotificationSetting.objects.filter(
                user=admin, type=None, organization=None
            ).count(),
            0,
        )

    def test_validate_global_notification_setting(self):
        admin = self._get_admin()
        with self.subTest("Test global notification setting creation"):
            NotificationSetting.objects.filter(
                user=admin, organization=None, type=None
            ).delete()
            global_setting = NotificationSetting(
                user=admin, organization=None, type=None, email=True, web=True
            )
            global_setting.full_clean()
            global_setting.save()
            self.assertIsNotNone(global_setting)

        with self.subTest("Test only one global notification setting per user"):
            global_setting = NotificationSetting(
                user=admin, organization=None, type=None, email=True, web=True
            )
            with self.assertRaises(ValidationError):
                global_setting.full_clean()
                global_setting.save()

    def test_new_org_creation_respects_global_preferences(self):
        """
        Regression test for bug 1 in https://github.com/openwisp/openwisp-notifications/issues/448
        """
        admin = self._get_admin()
        global_setting = NotificationSetting.objects.get(
            user=admin, organization=None, type=None
        )
        global_setting.web = False
        global_setting.email = False
        global_setting.full_clean()
        global_setting.save()
        org = self._create_org(name="New Test Org")
        org_setting = NotificationSetting.objects.get(
            user=admin, organization=org, type="default"
        )
        self.assertEqual(org_setting.web, False)
        self.assertEqual(org_setting.email, False)

        with self.subTest("global email=False, web=True"):
            global_setting.refresh_from_db()
            global_setting.email = False
            global_setting.web = True
            global_setting.save()
            org = self._create_org(name="Asymmetric Org Email False")
            org_setting = NotificationSetting.objects.get(
                user=admin, organization=org, type="default"
            )
            self.assertEqual(org_setting.email, False)
            self.assertEqual(org_setting.web, None)

    def test_org_admin_addition_respects_global_preferences(self):
        """
        Regression test for bug 2 in https://github.com/openwisp/openwisp-notifications/issues/448
        """
        user = self._get_user()
        org1 = self._get_org()
        self._create_org_user(user=user, organization=org1, is_admin=True)
        # Global notification setting is created only when the user is
        # admin of atleast one organization.
        global_setting = NotificationSetting.objects.get(
            user=user, organization=None, type=None
        )
        global_setting.web = False
        global_setting.email = False
        global_setting.full_clean()
        global_setting.save()
        # Updating global setting should update existing org settings
        org1_setting = NotificationSetting.objects.get(
            user=user, organization=org1, type="default"
        )
        self.assertEqual(org1_setting.web, False)
        self.assertEqual(org1_setting.email, False)
        # New organization should also respect global preferences
        org2 = self._create_org(name="New Test Org")
        self._create_org_user(user=user, organization=org2, is_admin=True)
        org2_setting = NotificationSetting.objects.get(
            user=user, organization=org2, type="default"
        )
        self.assertEqual(org2_setting.web, False)
        self.assertEqual(org2_setting.email, False)

        with self.subTest("global email=False, web=True"):
            new_user = self._create_operator()
            org_a = self._create_org(name="Asymmetric Add Org A")
            self._create_org_user(user=new_user, organization=org_a, is_admin=True)
            new_global = NotificationSetting.objects.get(
                user=new_user, organization=None, type=None
            )
            new_global.email = False
            new_global.web = True
            new_global.save()
            org_b = self._create_org(name="Asymmetric Add Org B")
            self._create_org_user(user=new_user, organization=org_b, is_admin=True)
            org_setting = NotificationSetting.objects.get(
                user=new_user, organization=org_b, type="default"
            )
            self.assertEqual(org_setting.email, False)
            self.assertEqual(org_setting.web, None)

    def test_org_setting_change_does_not_change_user_overrides(self):
        """
        Regression test for bug 3 in https://github.com/openwisp/openwisp-notifications/issues/448
        """
        admin = self._create_admin()
        org = self._get_org()
        global_setting = NotificationSetting.objects.get(
            user=admin, organization=None, type=None
        )
        # User explicitly disables web for this org
        org_setting = NotificationSetting.objects.get(
            user=admin, organization=org, type="default"
        )
        org_setting.web = False
        org_setting.full_clean()
        org_setting.save()
        org_setting.refresh_from_db()
        self.assertEqual(org_setting.web, False)

        # Toggle global web off and back on
        global_setting.web = False
        global_setting.full_clean()
        global_setting.save()
        global_setting.web = True
        global_setting.full_clean()
        global_setting.save()
        default_type_setting = NotificationSetting.objects.get(
            user=admin, organization=org, type="default"
        )
        self.assertEqual(default_type_setting.web_notification, True)

    def test_global_email_change_does_not_reset_user_web_override(self):
        admin = self._create_admin()
        org = self._get_org()
        global_setting = NotificationSetting.objects.get(
            user=admin,
            organization=None,
            type=None,
        )
        global_setting.web = True
        global_setting.email = True
        global_setting.full_clean()
        global_setting.save()
        notification_setting = NotificationSetting.objects.get(
            user=admin,
            organization=org,
            type="default",
        )
        notification_setting.web = False
        notification_setting.full_clean()
        notification_setting.save()
        notification_setting.refresh_from_db()
        self.assertEqual(notification_setting.web, False)
        # Change only global email preference
        global_setting.email = False
        global_setting.full_clean()
        global_setting.save()
        # Explicit user override must remain intact
        notification_setting.refresh_from_db()
        self.assertEqual(notification_setting.web, False)

    def test_global_toggle_does_not_override_type_email_default(self):
        admin = self._get_admin()
        org = self._get_org("default")
        generic_setting = NotificationSetting.objects.get(
            user=admin, organization=org, type="generic_message"
        )
        self.assertIsNone(generic_setting.email)
        self.assertEqual(generic_setting.email_notification, False)
        # Disable global email so all settings changes to False
        global_setting = NotificationSetting.objects.get(
            user=admin, organization=None, type=None
        )
        global_setting.email = False
        global_setting.full_clean()
        global_setting.save()
        # Enable email for global setting
        global_setting.email = True
        global_setting.full_clean()
        global_setting.save()
        generic_setting.refresh_from_db()
        self.assertIsNone(generic_setting.email)
        self.assertEqual(generic_setting.email_notification, False)

    def test_user_explicit_false_not_collapsed_when_type_enabled_default(self):
        admin = self._get_admin()
        org = self._get_org()
        notification_setting = NotificationSetting.objects.get(
            user=admin, organization=org, type="default"
        )
        self.assertEqual(notification_setting.type_config["email_notification"], True)
        # User explicitly disables email for this org
        notification_setting.email = False
        notification_setting.full_clean()
        notification_setting.save()
        notification_setting.refresh_from_db()
        self.assertEqual(notification_setting.email_notification, False)
        # Toggle organization notification settings
        org.notification_settings.email = False
        org.notification_settings.full_clean()
        org.notification_settings.save()
        org.notification_settings.email = True
        org.notification_settings.save()
        notification_setting.refresh_from_db()
        self.assertEqual(notification_setting.email, False)
        self.assertEqual(notification_setting.email_notification, False)

    def test_user_explicit_false_not_collapsed_on_web_when_type_enabled(self):
        admin = self._get_admin()
        org = self._get_org()
        notification_setting = NotificationSetting.objects.get(
            user=admin, organization=org, type="default"
        )
        self.assertEqual(notification_setting.type_config["web_notification"], True)
        # User explicitly disables web for this org
        notification_setting.web = False
        notification_setting.full_clean()
        notification_setting.save()
        notification_setting.refresh_from_db()
        self.assertEqual(notification_setting.web_notification, False)
        # Toggle organization notification settings
        org.notification_settings.web = False
        org.notification_settings.full_clean()
        org.notification_settings.save()
        org.notification_settings.web = True
        org.notification_settings.save()
        notification_setting.refresh_from_db()
        self.assertEqual(notification_setting.web, False)
        self.assertEqual(notification_setting.web_notification, False)

    def test_staff_user_created(self):
        user = self._create_user(
            username="staff", email="staff@example.com", is_staff=True
        )
        self.assertEqual(
            NotificationSetting.objects.filter(
                user=user, organization=None, type=None, deleted=False
            ).count(),
            1,
        )

    def test_user_promoted_to_staff(self):
        user = self._create_user(username="promote_staff", email="staff@example.com")
        self.assertEqual(NotificationSetting.objects.count(), 0)
        user.is_staff = True
        user.save()
        self.assertEqual(
            NotificationSetting.objects.filter(
                user=user, organization=None, type=None, deleted=False
            ).count(),
            1,
        )

    def test_create_superuser_notification_settings_skips_regular_user(self):
        user = self._create_user(
            username="regular_task", email="regular_task@example.com"
        )
        create_superuser_notification_settings.delay(user.pk)
        self.assertFalse(
            NotificationSetting.objects.filter(user=user).exists(),
            "Regular users must not get notification settings from this task.",
        )

    def test_staff_repromoted_reactivates_global_preference(self):
        user = self._create_user(
            username="staff_repromote",
            email="staff_repromote@example.com",
            is_staff=True,
        )
        global_ns = NotificationSetting.objects.get(user=user, organization=None)
        self.assertFalse(global_ns.deleted)
        user.is_staff = False
        user.save()
        global_ns.refresh_from_db()
        self.assertTrue(global_ns.deleted)
        user.is_staff = True
        user.save()
        global_ns.refresh_from_db()
        self.assertFalse(
            global_ns.deleted,
            "Re-promoting a staff user must reactivate the global setting.",
        )

    def test_staff_joins_org_retains_global_preference(self):
        user = self._create_user(username="staff_org", is_staff=True)
        org = self._get_org()
        global_ns = NotificationSetting.objects.get(user=user, organization=None)
        self.assertFalse(global_ns.deleted)
        org_user = OrganizationUser.objects.create(
            user=user, organization=org, is_admin=False
        )
        global_ns.refresh_from_db()
        self.assertFalse(
            global_ns.deleted,
            "Global setting was wiped when joining org as non-admin",
        )
        org_user.is_admin = True
        org_user.save()
        global_ns.refresh_from_db()
        self.assertFalse(
            global_ns.deleted, "Global setting was wiped when promoted to admin"
        )

    def test_superuser_and_staff_demoted_to_staff_only(self):
        user = self._create_user(username="both_priv", is_superuser=True, is_staff=True)
        self.assertTrue(
            NotificationSetting.objects.filter(user=user, deleted=False).count() > 1
        )
        user.is_superuser = False
        user.save()
        global_ns = NotificationSetting.objects.get(user=user, organization=None)
        self.assertFalse(
            global_ns.deleted, "Global setting was deleted on superuser demotion"
        )
        self.assertFalse(
            NotificationSetting.objects.filter(user=user, deleted=False)
            .exclude(organization=None)
            .exists(),
            "Org settings were not pruned on superuser demotion",
        )

    def test_staff_demoted_to_regular_user(self):
        user = self._create_user(username="staff_demote", is_staff=True)
        global_ns = NotificationSetting.objects.get(user=user, organization=None)
        self.assertFalse(global_ns.deleted)
        user.is_staff = False
        user.save()
        global_ns.refresh_from_db()
        self.assertTrue(
            global_ns.deleted,
            "Global setting was not deleted upon total privilege loss",
        )

    def test_staff_promoted_to_superuser(self):
        user = self._create_user(username="staff_to_super", is_staff=True)
        self.assertEqual(NotificationSetting.objects.filter(user=user).count(), 1)
        user.is_superuser = True
        user.save()
        self.assertTrue(NotificationSetting.objects.filter(user=user).count() > 1)
