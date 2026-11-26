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

    def fillEmail(self, email: str | None = None):
        if email is None:
            email = os.environ["TEST_USER_EMAIL"]
        self.page.get_by_role("textbox", name="Email").fill(email)

    def fillPassword(self, password: str | None = None):
        if password is None:
            password = os.environ["TEST_USER_PASSWORD"]
        self.page.get_by_role("textbox", name="Password").fill(password)

    def clickSignInButton(self):
        button = self.page.get_by_role("button", name="Sign in")
        button.click()

    def clickForgotPasswordLink(self):
        link = self.page.get_by_role("link", name="Forgot password?")
        link.click()
        expect(self.page.get_by_role("button", name="Send reset link")).to_be_visible()

