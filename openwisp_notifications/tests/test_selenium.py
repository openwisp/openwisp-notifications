import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from openwisp_notifications.swapper import swapper_load_model
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.test_selenium_mixins import SeleniumTestMixin

OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')


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
        org = self._create_org()
        OrganizationUser.objects.create(user=self.admin, organization=org)

    def open(self, url, driver=None):
        driver = self.driver or self.web_driver
        driver.get(f'{self.live_server_url}{url}')

    def test_notification_preference_page(self):
        self.login()
        self.open('/notifications/preferences/')
        time.sleep(0.1)

        # Uncheck the global web checkbox
        global_web_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'global-web'))
        )
        global_web_label = global_web_checkbox.find_element(By.XPATH, './parent::label')
        global_web_label.click()

        all_checkboxes = self.driver.find_elements(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        )
        for checkbox in all_checkboxes:
            self.assertFalse(checkbox.is_selected())

        # Check the org-level web checkbox
        org_level_web_checkbox = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'org-1-web'))
        )
        org_level_web_checkbox.click()

        web_checkboxes = self.driver.find_elements(
            By.CSS_SELECTOR, 'input[id^="org-1-web-"]'
        )
        for checkbox in web_checkboxes:
            self.assertTrue(checkbox.is_selected())

        # Check a single email checkbox
        first_org_email_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'org-1-email-1'))
        )
        first_org_email_checkbox.click()
        self.assertTrue(
            first_org_email_checkbox.find_element(By.TAG_NAME, 'input').is_selected()
        )
