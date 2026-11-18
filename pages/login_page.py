from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.consts import FILE_PATH


class LoginPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

    def fiilEmail(self):
        email = self.page.get_by_role("textbox", name="email")
        


