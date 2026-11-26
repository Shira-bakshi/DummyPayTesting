import pytest


@pytest.mark.regression
def test_unreadBadgeMatchesNotificationList(notifications):
    notifications.expectUnreadBadgeToMatchList()


@pytest.mark.regression
def test_allAndUnreadFiltersShowMatchingNotifications(notifications):
    notifications.expectUnreadBadgeToMatchList()
    notifications.selectNotificationsFilter("All")
    totalCount = notifications.notificationRows.count()
    unreadCount = notifications.getUnreadNotificationRows().count()

    notifications.selectNotificationsFilter("Unread")
    notifications.expectNotificationCounts(total=unreadCount, unread=unreadCount)

    notifications.selectNotificationsFilter("All")
    notifications.expectNotificationCounts(total=totalCount, unread=unreadCount)


@pytest.mark.regression
def test_markAllAsReadHidesUnreadBadge(notifications):
    notifications.expectUnreadBadgeToMatchList()
    if notifications.getUnreadBadgeCount() == 0:
        pytest.skip("The test account has no unread notifications to mark as read.")

    notifications.markAllAsRead()
    notifications.expectNoUnreadNotifications()
