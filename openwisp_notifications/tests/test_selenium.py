from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
from selenium.webdriver.common.by import By

from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.utils import _get_object_link, get_unsubscribe_url_for_user
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import SeleniumTestMixin

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')
Organization = swapper_load_model('openwisp_users', 'Organization')
OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')


@tag('test_selenium')
class TestSelenium(
    SeleniumTestMixin,
    TestOrganizationMixin,
    StaticLiveServerTestCase,
):
    def setUp(self):
        super().setUp()
        org = self._create_org()
        OrganizationUser.objects.create(user=self.admin, organization=org)
        self.operator = super()._get_operator()
        self.notification_options = dict(
            sender=self.admin,
            recipient=self.admin,
            verb='Test Notification',
            email_subject='Test Email subject',
            action_object=self.operator,
            target=self.operator,
            type='default',
        )

    def _create_notification(self):
        return notify.send(**self.notification_options)

    def test_notification_relative_link(self):
        self.login()
        notification = self._create_notification().pop()[1][0]
        self.find_element(By.ID, 'openwisp_notifications').click()
        self.wait_for_visibility(By.CLASS_NAME, 'ow-notification-elem')
        notification_elem = self.find_element(By.CLASS_NAME, 'ow-notification-elem')
        data_location_value = notification_elem.get_attribute('data-location')
        self.assertEqual(
            data_location_value, _get_object_link(notification.target, False)
        )

    def test_notification_dialog(self):
        self.login()
        self.notification_options.update(
            {'message': 'Test Message', 'description': 'Test Description'}
        )
        notification = self._create_notification().pop()[1][0]
        self.find_element(By.ID, 'openwisp_notifications').click()
        self.wait_for_visibility(By.ID, f'ow-{notification.id}')
        self.find_element(By.ID, f'ow-{notification.id}').click()
        self.wait_for_visibility(By.CLASS_NAME, 'ow-dialog-notification')
        dialog = self.find_element(By.CLASS_NAME, 'ow-dialog-notification')
        self.assertEqual(
            dialog.find_element(By.CLASS_NAME, 'ow-message-title').text, 'Test Message'
        )
        self.assertEqual(
            dialog.find_element(By.CLASS_NAME, 'ow-message-description').text,
            'Test Description',
        )

    def test_notification_dialog_open_button_visibility(self):
        self.login()
        self.notification_options.pop('target')
        self.notification_options.update(
            {'message': 'Test Message', 'description': 'Test Description'}
        )
        notification = self._create_notification().pop()[1][0]
        self.find_element(By.ID, 'openwisp_notifications').click()
        self.find_element(By.ID, f'ow-{notification.id}').click()
        dialog = self.find_element(By.CLASS_NAME, 'ow-dialog-notification')
        # This confirms the button is hidden
        dialog.find_element(By.CSS_SELECTOR, '.ow-message-target-redirect.ow-hide')

    def test_email_unsubscribe_page(self):
        with self.subTest('Token is invalid'):
            self.open(reverse('notifications:unsubscribe'))
            self.assertEqual(
                self.find_element(By.TAG_NAME, 'h2').text, 'Invalid or Expired Link'
            )

        with self.subTest('User unsubscribe with valid URL'):
            unsubscribe_link = get_unsubscribe_url_for_user(self.admin, False)
            self.open(unsubscribe_link)
            self.wait_for_visibility(By.ID, 'subscribed-message')
            self.wait_for_invisibility(By.ID, 'unsubscribed-message')
            toggle_btn = self.find_element(By.ID, 'toggle-btn')
            self.assertEqual(toggle_btn.text, 'Unsubscribe')
            toggle_btn.click()
            self.wait_for_visibility(By.ID, 'confirm-unsubscribed')
            self.wait_for_invisibility(By.ID, 'confirm-subscribed')
            self.assertEqual(self.find_element(By.ID, 'toggle-btn').text, 'Subscribe')

        with self.subTest('User subscribe to notifications again'):
            self.open(unsubscribe_link)
            self.wait_for_visibility(By.ID, 'unsubscribed-message')
            self.wait_for_invisibility(By.ID, 'subscribed-message')
            toggle_btn = self.find_element(By.ID, 'toggle-btn')
            self.assertEqual(toggle_btn.text, 'Subscribe')
            toggle_btn.click()
            self.wait_for_visibility(By.ID, 'confirm-subscribed')
            self.wait_for_invisibility(By.ID, 'confirm-unsubscribed')
            self.assertEqual(self.find_element(By.ID, 'toggle-btn').text, 'Unsubscribe')

        with self.subTest('Network request fails'):
            self.open(unsubscribe_link)
            self.web_driver.execute_script(
                """
                window.fetch = function() {
                    return Promise.reject(new Error('Simulated fetch failure'));
                };
            """
            )
            self.web_driver.find_element(By.ID, 'toggle-btn').click()
            self.wait_for_visibility(By.ID, 'error-msg')

    def test_notification_preference_page(self):
        self.login()
        self.open(reverse('notifications:notification_preference'))

        with self.subTest('Notifications are enabled'):
            # Expand the first organization panel
            self.find_element(By.CSS_SELECTOR, '.toggle-icon').click()
            # All web notifications are enabled
            web_checkboxes = self.find_elements(
                By.CSS_SELECTOR,
                'input[type="checkbox"][data-column="web"]',
                wait_for='presence',
            )
            for checkbox in web_checkboxes:
                self.assertEqual(checkbox.is_selected(), True)
            # Email notification is enabled for default type
            default_email_checkbox = self.find_element(
                By.CSS_SELECTOR,
                'label#org-1-email-1 input',
                wait_for='presence',
            )
            self.assertTrue(default_email_checkbox.is_selected())
            # Email notification is disabled for generic type
            generic_email_checkbox = self.find_element(
                By.CSS_SELECTOR,
                'label#org-1-email-2 input',
                wait_for='presence',
            )
            self.assertFalse(generic_email_checkbox.is_selected())

        with self.subTest('Disabling global notification setting'):
            self.find_element(
                By.CSS_SELECTOR,
                '.global-setting-dropdown[data-web-state] .global-setting-dropdown-toggle',
            ).click()
            self.find_element(
                By.CSS_SELECTOR,
                '.global-setting-dropdown[data-web-state]'
                ' .global-setting-dropdown-menu button:last-child',
            ).click()
            self.find_element(By.CSS_SELECTOR, '#confirmation-modal #confirm').click()

            all_checkboxes = self.find_elements(
                By.CSS_SELECTOR, 'input[type="checkbox"]', wait_for='presence'
            )
            for checkbox in all_checkboxes:
                self.assertFalse(checkbox.is_selected())
                # Verify database has NotificationSetting.web set to False
                if pk := checkbox.get_attribute('data-pk'):
                    self.assertEqual(NotificationSetting.objects.get(pk=pk).web, False)

        with self.subTest('Enabling organization-level web notification'):
            # Check the org-level web checkbox
            org_level_web_checkbox = self.find_element(By.CSS_SELECTOR, '#org-1-web')
            org_level_web_checkbox.click()

            # Verify that all web checkboxes under org-1 are selected
            web_checkboxes = self.find_elements(
                By.CSS_SELECTOR, 'label[id^="org-1-web-"] input', wait_for='presence'
            )
            for checkbox in web_checkboxes:
                self.assertTrue(checkbox.is_selected())
                self.assertEqual(NotificationSetting.objects.get(pk=pk).web, True)

        with self.subTest('Enabling single email notification'):
            first_org_email_checkbox = self.find_element(By.ID, 'org-1-email-1')
            first_org_email_checkbox.click()
            input = first_org_email_checkbox.find_element(By.TAG_NAME, 'input')
            self.assertTrue(input.is_selected())
            self.assertEqual(
                NotificationSetting.objects.get(
                    pk=input.get_attribute('data-pk')
                ).email,
                True,
            )

    def test_empty_notification_preference_page(self):
        # Delete all organizations
        Organization.objects.all().delete()

        self.login()
        self.open(reverse('notifications:notification_preference'))

        no_organizations_element = self.wait_for_visibility(
            By.CLASS_NAME, 'no-organizations'
        )
        self.assertEqual(
            no_organizations_element.text,
            'No organizations available.',
        )
