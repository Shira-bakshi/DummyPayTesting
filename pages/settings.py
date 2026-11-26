
import os
import re

from playwright.sync_api import Locator, expect

from pages.basePage import BasePage
from utilities.consts import CURRENCY, FILE_PATH
from dotenv import load_dotenv


class SettingsPage(BasePage):
    load_dotenv()
    def open(self):
        self.openPage(f"{FILE_PATH.rstrip('/')}/settings")

    # def checkDetails(self):
    #     email = self.page.get_by_role()
    #     assert os.getenv("TEST_USER_EMAIL") == 

    @property
    def currencyDropdown(self) -> Locator:
        return self.page.get_by_role("combobox", name="Currency", exact=True)

    @property
    def currencyChangeButton(self) -> Locator:
        return self.page.get_by_role("button", name="Change", exact=True)

    def getPreferredCurrency(self) -> CURRENCY:
        profileCurrency = self.page.locator('dt:text-is("Preferred currency") + dd')
        expect(profileCurrency).to_have_text(re.compile(r"^[A-Z]{3}\b"))
        return CURRENCY(profileCurrency.inner_text().split()[0])

    def selectCurrency(self, currency: CURRENCY) -> None:
        self.currencyDropdown.click()
        self.page.get_by_role("option", name=re.compile(rf"^{currency.value}\b")).click()

    def expectSelectedCurrency(self, currency: CURRENCY) -> None:
        expect(self.currencyDropdown).to_have_text(re.compile(rf"^{currency.value}\b"))

    def expectCurrencyChangeDisabled(self) -> None:
        expect(self.currencyChangeButton).to_be_visible()
        expect(self.currencyChangeButton).to_be_disabled()

    def expectCurrencyChangeClickable(self) -> None:
        self.currencyChangeButton.click(trial=True)

    @property
    def displayNameField(self) -> Locator:
        return self.page.get_by_role("textbox", name="Display name", exact=True)

    @property
    def displayNameSaveButton(self) -> Locator:
        return self.page.get_by_role("button", name="Save", exact=True)

    def getDisplayName(self) -> str:
        return self.displayNameField.input_value()

    def fillDisplayName(self, name: str) -> None:
        self.displayNameField.fill(name)

    def expectDisplayNameSaveDisabled(self) -> None:
        expect(self.displayNameSaveButton).to_be_visible()
        expect(self.displayNameSaveButton).to_be_disabled()

    def expectDisplayNameSaveClickable(self) -> None:
        self.displayNameSaveButton.click(trial=True)

    def saveDisplayName(self) -> None:
        self.displayNameSaveButton.click()

    def expectDisplayNameError(self, message: str) -> None:
        expect(self.page.get_by_text(message, exact=True)).to_be_visible()

    def expectSavedDisplayName(self, name: str) -> None:
        profileName = self.page.locator('dt:text-is("Display name") + dd')
        expect(profileName).to_have_text(name)
        expect(self.displayNameField).to_have_value(name)

    
