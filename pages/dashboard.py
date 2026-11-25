import re
from decimal import Decimal

from playwright.sync_api import expect

from pages.basePage import BasePage
from utilities.consts import CURRENCY, FILE_PATH


class DashboardPage(BasePage):

    def open(self):
        self.openPage(FILE_PATH)

    @staticmethod
    def parseDisplayedBalance(text: str) -> Decimal:
        amount = re.search(r"\d[\d,]*\.\d{2}\b", text)
        assert amount, f"Expected a monetary amount, got {text!r}"
        value = Decimal(amount.group().replace(",", ""))
        return -value if re.search(r"[-−(]", text) else value

    def getTotalBalance(self) -> tuple[CURRENCY, Decimal, int]:
        card = self.page.get_by_test_id("total-balance")
        details = card.locator('[data-slot="card-content"]')
        pattern = re.compile(r"(\d+) wallets?\s*·\s*shown in ([A-Z]{3})")
        expect(details).to_have_text(pattern)
        match = pattern.search(details.inner_text())
        assert match, "The total balance card must show a wallet count and a display currency"
        count, currency = match.groups()
        amount = self.parseDisplayedBalance(card.locator('[data-slot="card-title"]').inner_text())
        return CURRENCY(currency), amount, int(count)

    def getWalletBalances(self, expected_count: int) -> dict[CURRENCY, Decimal]:
        cards = self.page.locator('[data-testid^="wallet-"][data-slot="card"]')
        expect(cards).to_have_count(expected_count)
        balances = {}
        for card in cards.all():
            currency = CURRENCY(card.get_attribute("data-testid").removeprefix("wallet-"))
            amount = card.locator('p:text-is("Available balance") + p').inner_text()
            assert currency not in balances, f"Duplicate wallet for {currency}"
            balances[currency] = self.parseDisplayedBalance(amount)
        return balances

    def getExchangeRate(self, base: CURRENCY, target: CURRENCY) -> Decimal:
        label = re.compile(rf"^1\s+{base.value}\s*→\s*{target.value}$")
        row = self.page.get_by_test_id("rates-card").get_by_role("listitem").filter(
            has=self.page.get_by_text(label)
        )
        rate = row.get_by_text(re.compile(r"^\d+\.\d+$"))
        expect(rate).to_be_visible()
        return Decimal(rate.inner_text().strip())

    def openNotifications(self):
        # self.page.pause()
        navigation = self.page.get_by_role("navigation", name="Main")
        navigation.locator('a[href="/notifications"]').click()

    def openRecentTransactions(self):
        navigation = self.page.get_by_role("navigation", name="Main")
        navigation.locator('a[href="/history"]').click()   

    def openSendMoneyButton(self):
        self.page.get_by_role("link", name="Send money", exact=True).click() 
       
