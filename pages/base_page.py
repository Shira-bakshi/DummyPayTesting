from playwright.sync_api import Page


class BasePage:

    def __init__(self, page: Page):
        self.page = page

    def openPage(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")

    def getTitle(self):
        return self.page.title()