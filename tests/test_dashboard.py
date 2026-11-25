from decimal import Decimal

import pytest
from playwright.sync_api import expect

from pages.dashboard import DashboardPage
from utilities.consts import CURRENCY, FILE_PATH


CURRENCY_SYMBOLS = {
    CURRENCY.USD: "$",
    CURRENCY.ILS: "₪",
    CURRENCY.EUR: "€",
    CURRENCY.GBP: "£",
}


def calculateTotalBalanceRange(
    dashboard: DashboardPage,
    displayCurrency: CURRENCY,
    balances: dict[CURRENCY, Decimal],
) -> tuple[Decimal, Decimal]:
    minimumTotal = maximumTotal = balances.get(displayCurrency, Decimal("0"))
    convertedBalances = []

    for currency, balance in balances.items():
        walletAmount = f"{CURRENCY_SYMBOLS[currency]}{balance:,.2f}"
        if currency == displayCurrency:
            print(f"[WALLET] {currency}: {walletAmount} (display currency, no conversion)")
            convertedBalances.append(balance)
            continue

        rate = dashboard.getExchangeRate(displayCurrency, currency)
        # The displayed rate is rounded, so allow half a unit at its last decimal place.
        rateMargin = Decimal("0.5").scaleb(rate.as_tuple().exponent)
        assert rate > rateMargin, f"Invalid exchange rate for {currency}: {rate}"
        converted = balance / rate
        convertedBalances.append(converted)
        print(
            f"[WALLET] {currency}: {walletAmount} | 1 {displayCurrency} = {rate} {currency} | "
            f"{balance:,.2f} / {rate} = {CURRENCY_SYMBOLS[displayCurrency]}{converted:,.6f}"
        )
        convertedAtLowRate = balance / (rate - rateMargin)
        convertedAtHighRate = balance / (rate + rateMargin)
        minimumTotal += min(convertedAtLowRate, convertedAtHighRate)
        maximumTotal += max(convertedAtLowRate, convertedAtHighRate)

    # The total itself is displayed to the nearest cent.
    displayMargin = Decimal("0.005")
    terms = " + ".join(f"({balance:,.6f})" for balance in convertedBalances) or "0"
    print(f"[CALC] {terms} = {sum(convertedBalances, Decimal('0')):,.6f} {displayCurrency}")
    return minimumTotal - displayMargin, maximumTotal + displayMargin


@pytest.mark.regression
def test_dashboardTotalBalanceMatchesConvertedWallets(dashboard: DashboardPage):
    displayCurrency, displayedTotal, walletCount = dashboard.getTotalBalance()
    print(f"[CHECK] Converting {walletCount} wallet(s) to {displayCurrency}.")
    balances = dashboard.getWalletBalances(walletCount)
    minimumTotal, maximumTotal = calculateTotalBalanceRange(dashboard, displayCurrency, balances)
    print(
        f"[COMPARE] Dashboard: {CURRENCY_SYMBOLS[displayCurrency]}{displayedTotal:,.2f} "
        f"{displayCurrency} | Expected range after rounding: "
        f"{minimumTotal:,.6f} to {maximumTotal:,.6f} {displayCurrency}"
    )

    assert minimumTotal <= displayedTotal <= maximumTotal, (
        f"Displayed total {displayedTotal} {displayCurrency} does not match "
        f"the calculated range {minimumTotal:.6f}–{maximumTotal:.6f} "
        f"after accounting for rounding. Wallet balances: {balances}"
    )
    print("[OK] The displayed total is within the expected range.")


@pytest.mark.smoke
def test_dashboardOpensNotifications(dashboard):
    dashboard.openNotifications()
    expect(dashboard.page).to_have_url(f"{FILE_PATH}notifications")


@pytest.mark.smoke
def test_dashboardOpensRecentTransactions(dashboard):
    dashboard.openRecentTransactions()
    expect(dashboard.page).to_have_url(f"{FILE_PATH}history")


@pytest.mark.smoke
def test_dashboardSendMoney(dashboard):
    dashboard.openSendMoneyButton()
    expect(dashboard.page).to_have_url(f"{FILE_PATH}send")


