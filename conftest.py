import pytest
from playwright.sync_api import Page
from pages.historyPage import historyPage

from pages.dashboard import DashboardPage
from pages.loginPage import LoginPage
from pages.notifications import NotificationsPage
from pages.sendMoney import SendMoneyPage
from pages.settings import SettingsPage
from utilities.backend.browserAuth import createAuthStorageState


def pytest_runtest_logstart(nodeid: str) -> None:
    print(f"\n[TEST] {nodeid}", flush=True)


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    # Compatibility with pytest 9.2 for the pytest-playwright fallback fixture.
    return pytestconfig.getoption("--base-url") or pytestconfig.getini("base_url") or None


@pytest.fixture
def loginPage(page: Page) -> LoginPage:
    print("[SETUP] Opening sign-in form for the UI login test.", flush=True)
    return LoginPage(page)


@pytest.fixture
def authenticatedPage(new_context) -> Page:
    print("[SETUP] Signing in through the API.", flush=True)
    context = new_context(storage_state=createAuthStorageState())
    return context.new_page()

@pytest.fixture
def sendMoneyPage(authenticatedPage: Page) -> SendMoneyPage:
    print("[SETUP] Opening Send Money.", flush=True)
    sendMoney = SendMoneyPage(authenticatedPage)
    sendMoney.open()
    return sendMoney

@pytest.fixture
def dashboard(authenticatedPage: Page) -> DashboardPage:
    print("[SETUP] Opening Dashboard.", flush=True)
    dashboardPage = DashboardPage(authenticatedPage)
    dashboardPage.open()
    return dashboardPage


@pytest.fixture
def settings(authenticatedPage: Page) -> SettingsPage:
    print("[SETUP] Opening Profile & Settings.", flush=True)
    settingsPage = SettingsPage(authenticatedPage)
    settingsPage.open()
    return settingsPage

@pytest.fixture
def notifications(authenticatedPage: Page) -> NotificationsPage:
    print("[SETUP] Opening Notifications.", flush=True)
    notificationPage = NotificationsPage(authenticatedPage)
    notificationPage.open()
    return notificationPage



@pytest.fixture
def history(authenticatedPage: Page) -> historyPage:
    history = historyPage(authenticatedPage)
    history.open()
    return history
