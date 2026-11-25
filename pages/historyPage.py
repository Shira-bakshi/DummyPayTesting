
import re

from playwright.sync_api import Locator, expect

from pages.basePage import BasePage
from utilities.consts import CURRENCY, FILE_PATH


class historyPage(BasePage):
    def open(self):
            self.openPage(f"{FILE_PATH.rstrip('/')}/history")
    
    def selectTransactionType(self, transactionType: str) -> None:
        dropdown = self.page.get_by_role("combobox", name="Type", exact=True)
        dropdown.click()
        self.page.get_by_role("option", name=transactionType, exact=True).click()


    def selectCurrency(self, currency: CURRENCY) -> None:
        self.currencyDropdown.click()
        self.page.get_by_role("option", name=currency.value, exact=True).click()
        expect(self.currencyDropdown).to_have_text(currency.value)

    @property
    def currencyDropdown(self) -> Locator:
        return self.page.get_by_role("combobox", name="Currency", exact=True)

    def setDateRange(self, fromDate: str, toDate: str) -> None:
        self.page.locator("#filter-from").fill(fromDate)
        self.page.locator("#filter-to").fill(toDate)    

    def clearFilters(self):
        self.page.get_by_role("button", name="Clear", exact=True).click()

    def expectDefaultFilters(self):
        expect(self.page.locator("#filter-from")).to_have_value("")
        expect(self.page.locator("#filter-to")).to_have_value("")

        typeDropdown = self.page.get_by_role("combobox", name="Type", exact=True)
        expect(typeDropdown).to_have_text("All types")
        expect(self.currencyDropdown).to_have_text("All currencies")

    def getVisibleTransactions(self)->Locator:
        return self.page.get_by_test_id("transaction-row")

    @property
    def transactionDetails(self) -> Locator:
        return self.page.get_by_role("dialog")

    def openTransactionDetails(self, row: Locator) -> None:
        row.click()
        expect(self.transactionDetails).to_be_visible()

    def closeTransactionDetails(self) -> None:
        self.transactionDetails.get_by_role("button", name="Close", exact=True).click()
        expect(self.transactionDetails).to_be_hidden()

    def getTransactionCount(self)->int:
        counter = self.page.get_by_role("main").get_by_text(
            re.compile(r"^\d+ transactions?$")
        )
        return int(counter.inner_text().split()[0])

    def getPaginationButton(self, name:str)-> Locator:
        return self.page.get_by_role("main").get_by_role(
            "button", name=name, exact=True)

    def goToNextPage(self) -> None:
        self.getPaginationButton("Next").click()

    def expectNoNextPage(self) -> None:
        nextButton = self.getPaginationButton("Next")
        expect(nextButton.and_(self.page.locator(":enabled"))).to_be_hidden()


    def goToPreviousPage(self) -> None:
        self.getPaginationButton("Previous").click() 

    def expectVisibleTransactionCount(self, count: int) -> None:
       expect(self.getVisibleTransactions()).to_have_count(count)

    def expectCurrentPage(self, pageNumber: int, totalPages: int) -> None:
        indicator = self.page.get_by_role("main").get_by_text(
            f"Page {pageNumber} of {totalPages}", exact=True
        )
        expect(indicator).to_be_visible()

    def expectNoMatchingTransactions(self) -> None:
        emptyState = self.page.get_by_role("main").get_by_text(
            "No matching transactions", exact=True
        )
        expect(emptyState).to_be_visible()
        self.expectVisibleTransactionCount(0)
        self.expectNoNextPage()
