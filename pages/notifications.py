
import re

from playwright.sync_api import Locator, expect

from pages.basePage import BasePage
from utilities.consts import FILE_PATH


class NotificationsPage(BasePage):

    def open(self):
        self.openPage(f"{FILE_PATH.rstrip('/')}/notifications")

    @property
    def notificationRows(self) -> Locator:
        return self.page.get_by_role("main").get_by_role("listitem")

    def getUnreadNotificationRows(self) -> Locator:
        return self.notificationRows.filter(
            has=self.page.get_by_role("button", name="Mark read", exact=True)
        )

    def selectNotificationsFilter(self, label: str) -> None:
        filters = self.page.get_by_role("radiogroup", name="Show notifications")
        option = filters.get_by_role("radio", name=re.compile(rf"^{re.escape(label)}(?: \(\d+\))?$"))
        option.click()
        expect(option).to_be_checked()

    def expectNotificationCounts(self, total: int, unread: int) -> None:
        expect(self.notificationRows).to_have_count(total)
        expect(self.getUnreadNotificationRows()).to_have_count(unread)

    @property
    def unreadBadge(self) -> Locator:
        navigation = self.page.get_by_role("navigation", name="Main")
        return navigation.get_by_test_id("unread-badge")

    def getUnreadBadgeCount(self) -> int:
        badge = self.unreadBadge
        if not badge.is_visible():
            return 0
        return int(badge.inner_text().split()[0])

    def expectUnreadBadgeToMatchList(self) -> None:
        # The badge and list can both appear empty while notifications are loading.
        self.page.wait_for_load_state("networkidle")
        unreadRows = self.getUnreadNotificationRows()
        badgeCount = self.getUnreadBadgeCount()
        expect(unreadRows).to_have_count(badgeCount)

    def markAllAsRead(self) -> None:
        self.page.get_by_role("button", name="Mark all as read", exact=True).click()

    def expectNoUnreadNotifications(self) -> None:
        expect(self.unreadBadge).to_be_hidden()
        expect(self.getUnreadNotificationRows()).to_have_count(0)
