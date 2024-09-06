import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

    def test_notification_preference_page(self):
        self.login()
        self.open('/notifications/preferences/')
        time.sleep(0.1)

        # Uncheck the global web checkbox
        global_web_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'global-web'))
        )

        self.driver.execute_script(
            """
            arguments[0].checked = false;
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            global_web_checkbox,
        )

        all_checkboxes = self.driver.find_elements(
            By.CSS_SELECTOR, 'input[type="checkbox"]'
        )
        for checkbox in all_checkboxes:
            self.assertFalse(checkbox.is_selected())

        # Check the org level web checkbox
        org_level_email_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[3]/div[3]/div/div[1]/div[2]/div[3]/div[1]/div/table/thead/tr/th[2]/div/label/span',
                )
            )
        )
        org_level_email_checkbox.click()

        web_checkboxes = self.driver.find_elements(
            By.XPATH,
            '//div[3]/div[3]/div/div[1]/div[2]/div[3]/div[1]/div/table/tbody//input[@class="web-checkbox"]',
        )

        for checkbox in web_checkboxes:
            self.assertTrue(checkbox.is_selected())

        # Check a single email checkbox
        first_org_email_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[3]/div[3]/div/div[1]/div[2]/div[3]/div[1]/div/table/tbody/tr[1]/td[3]/label/span',
                )
            )
        )
        first_org_email_checkbox.click()

        is_first_org_email_checkbox = self.driver.find_element(
            By.XPATH,
            '//div[3]/div[3]/div/div[1]/div[2]/div[3]/div[1]/div/table/tbody/tr[1]/td[3]/label//input',
        )
        self.assertTrue(is_first_org_email_checkbox.is_selected())
