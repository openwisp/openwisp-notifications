from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from openwisp_notifications.swapper import load_model
from openwisp_notifications.utils import _get_object_link
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.test_selenium_mixins import SeleniumTestMixin

Notification = load_model('Notification')


class TestWidget(
    SeleniumTestMixin,
    TestOrganizationMixin,
    StaticLiveServerTestCase,
):
    serve_static = True

    def setUp(self):
        self.admin = self._create_admin(
            username=self.admin_username, password=self.admin_password
        )

    def test_notification_relative_link(self):
        self.login()
        operator = super()._create_operator()
        data = dict(
            email_subject='Test Email subject',
            url='http://localhost:8000/admin/',
        )
        notification = Notification.objects.create(
            actor=self.admin,
            recipient=self.admin,
            description='Test Notification Description',
            verb='Test Notification',
            action_object=operator,
            target=operator,
            data=data,
        )
        self.web_driver.implicitly_wait(10)
        WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'openwisp_notifications'))
        )
        self.web_driver.find_element(By.ID, 'openwisp_notifications').click()
        WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'ow-notification-elem'))
        )
        notification_elem = self.web_driver.find_element(
            By.CLASS_NAME, 'ow-notification-elem'
        )
        data_location_value = notification_elem.get_attribute('data-location')
        self.assertEqual(
            data_location_value, _get_object_link(notification, 'target', False)
        )
