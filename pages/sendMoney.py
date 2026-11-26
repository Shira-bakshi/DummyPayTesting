from playwright.sync_api import Page, expect
from utilities.consts import FILE_PATH
from pages.basePage import BasePage

class SendMoneyPage(BasePage):
    def open(self):
        self.openPage(f"{FILE_PATH.rstrip('/')}/send")


    def fillEmail(self, email):
        field = self.page.get_by_role("textbox", name="Recipient's email")
        field.fill(email)
    def clickFindRecipient(self):
        button = self.page.get_by_role("button", name="Find recipient")
        expect(button).to_be_visible()
        button.click()

    def clickContinue(self):
        button = self.page.get_by_role("button", name="Continue")
        expect(button).to_be_visible()
        button.click()

    def expectUnknownRecipientRejected(self) -> None:
        main = self.page.get_by_role("main")
        alert = main.get_by_role("alert")
        expect(alert).to_have_text("No registered user found with this email address.")
        expect(main.get_by_role("textbox", name="Recipient's email")).to_be_visible()
        expect(main.get_by_role("button", name="Continue", exact=True)).to_be_hidden()


    
    
