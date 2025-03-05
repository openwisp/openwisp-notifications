from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from selenium.webdriver.common.by import By

from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.utils import _get_object_link
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import SeleniumTestMixin

Notification = load_model('Notification')
Organization = swapper_load_model('openwisp_users', 'Organization')
OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')


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
            data_location_value, _get_object_link(notification, 'target', False)
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

    def test_notification_preference_page(self):
        self.login()
        self.open('/notifications/preferences/')
        # Uncheck the global web checkbox
        WebDriverWait(self.web_driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    '.global-setting-dropdown[data-web-state] .global-setting-dropdown-toggle',
                )
            )
        ).click()
        WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    '.global-setting-dropdown[data-web-state]'
                    ' .global-setting-dropdown-menu button:last-child',
                )
            )
        ).click()

        WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '#confirmation-modal #confirm')
            )
        ).click()
        all_checkboxes = self.web_driver.find_elements(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        )
        for checkbox in all_checkboxes:
            self.assertFalse(checkbox.is_selected())

        # Expand the first organization panel if it's collapsed
        first_org_toggle = WebDriverWait(self.web_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.module .toggle-header'))
        )
        first_org_toggle.click()

        # Check the org-level web checkbox
        org_level_web_checkbox = WebDriverWait(self.web_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#org-1-web'))
        )
        org_level_web_checkbox.click()

        # Verify that all web checkboxes under org-1 are selected
        web_checkboxes = self.web_driver.find_elements(
            By.CSS_SELECTOR, 'input[id^="org-1-web-"]'
        )
        for checkbox in web_checkboxes:
            self.assertTrue(checkbox.is_displayed())
            self.assertTrue(checkbox.is_selected())

        # Check a single email checkbox
        first_org_email_checkbox = WebDriverWait(self.web_driver, 10).until(
            EC.presence_of_element_located((By.ID, 'org-1-email-1'))
        )
        first_org_email_checkbox.click()
        self.assertTrue(
            first_org_email_checkbox.find_element(By.TAG_NAME, 'input').is_selected()
        )

    def test_empty_notification_preference_page(self):
        # Delete all organizations
        Organization.objects.all().delete()

        self.login()
        self.open('/notifications/preferences/')

        no_organizations_element = WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'no-organizations'))
        )
        self.assertEqual(
            no_organizations_element.text,
            'No organizations available.',
        )
