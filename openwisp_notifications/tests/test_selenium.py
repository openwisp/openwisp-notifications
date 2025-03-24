from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from selenium.webdriver.common.by import By

from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model
from openwisp_notifications.utils import _get_object_link
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import SeleniumTestMixin

Notification = load_model('Notification')


@tag('selenium_tests')
class TestNotificationUi(
    SeleniumTestMixin,
    TestOrganizationMixin,
    StaticLiveServerTestCase,
):
    def setUp(self):
        super().setUp()
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
