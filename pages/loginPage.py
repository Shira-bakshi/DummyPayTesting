from playwright.sync_api import Page, expect

from pages.basePage import BasePage
from utilities.consts import FILE_PATH
import os
from dotenv import load_dotenv

class LoginPage(BasePage):
    load_dotenv()

    def __init__(self, page: Page):
        super().__init__(page)
        super().openPage(FILE_PATH)

    def fillEmail(self):
        email = self.page.get_by_role("textbox", name="Email")
        email.fill(os.getenv("TEST_USER_EMAIL"))

    def fillPassword(self):
        password = self.page.get_by_role("textbox", name="Password")
        password.fill(os.getenv("TEST_USER_PASSWORD"))

    def clickSignInButton(self):
        button = self.page.get_by_role("button", name="Sign in")
        button.click()

    def clickForgotPasswordLink(self):
        link = self.page.get_by_role("link", name="Forgot password?")
        link.click()
        expect(self.page.get_by_role("button", name="Send reset link")).to_be_visible()

