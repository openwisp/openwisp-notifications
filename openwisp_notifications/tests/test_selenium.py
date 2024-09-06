from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from openwisp_notifications.utils import generate_unsubscribe_link
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.test_selenium_mixins import SeleniumTestMixin


class TestSelenium(
    SeleniumTestMixin,
    TestOrganizationMixin,
    StaticLiveServerTestCase,
):
    serve_static = True

    def setUp(self):
        self.admin = self._create_admin(
            username=self.admin_username, password=self.admin_password
        )
        self.driver = self.web_driver

    def open(self, url, driver=None):
        driver = self.driver or self.web_driver
        driver.get(f'{self.live_server_url}{url}')

    def test_email_unsubscribe_page(self):
        unsubscribe_link = generate_unsubscribe_link(self.admin, False)
        self.open(unsubscribe_link)
        WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'toggle-btn'))
        )
        self.assertEqual(
            self.driver.find_element(By.ID, 'toggle-btn').text,
            'Unsubscribe',
        )

        # Unsubscribe
        self.driver.find_element(By.ID, 'toggle-btn').click()
        WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'confirmation-msg'))
        )
        self.assertEqual(
            self.driver.find_element(By.ID, 'confirmation-msg').text,
            'Successfully unsubscribed',
        )
        self.assertEqual(
            self.driver.find_element(By.ID, 'toggle-btn').text,
            'Subscribe',
        )

        # Re-subscribe
        self.driver.find_element(By.ID, 'toggle-btn').click()
        WebDriverWait(self.web_driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'confirmation-msg'))
        )
        self.assertEqual(
            self.driver.find_element(By.ID, 'confirmation-msg').text,
            'Successfully subscribed',
        )
        self.assertEqual(
            self.driver.find_element(By.ID, 'toggle-btn').text,
            'Unsubscribe',
        )
