# DummyPay Software Test Description

*STD  |  Version 1.0  |  November 26, 2026*

This document maps all 29 collected cases to their source files, inputs, steps, and expected results. Bracketed values are pytest parameter IDs. A run also includes a browser ID.

## How to Use This Document

Set up the test environment using the README and STP. Prepare the data described for each module. After the run, compare expected and actual results in [the full test report](../reports/test-report.html).

## Coverage and Traceability

The suite covers login (3), dashboard (4), history (6), notifications (3), transfers (4), and settings (9). Both sign-in tests and the three dashboard navigation tests are Smoke tests. The remaining cases are Regression tests.

## Login

`tests/test_login.py`

Use the sign-in form with the test account.

### LGN-01  ·  Invalid sign-in

`test_negativeLoginPage`

Submit a valid account email with an incorrect password, then submit a value that is outside the email format. Both attempts leave the browser on the login page.

### LGN-02  ·  Valid sign-in

`test_loginPage`

Enter the test account email and password and select Sign in. The Main navigation becomes visible.

### LGN-03  ·  Password reset navigation

`test_forgotPassword`

Select the password reset link. The expected destination is /forgot-password. The test is marked Skip.

## Dashboard

`tests/test_dashboard.py`

Use an authenticated browser context.

### DSH-01  ·  Total balance

`test_dashboardTotalBalanceMatchesConvertedWallets`

Read the wallet balances, display currency, and exchange rates. The displayed total falls within the range calculated using Decimal, including tolerances for rounding the rates and the total.

### DSH-02  ·  Open notifications

`test_dashboardOpensNotifications`

Open notifications from the dashboard. The URL ends in /notifications.

### DSH-03  ·  Open transaction history

`test_dashboardOpensRecentTransactions`

Open recent transactions from the dashboard. The URL ends in /history.

### DSH-04  ·  Open Send Money

`test_dashboardSendMoney`

Select Send Money on the dashboard. The URL ends in /send.

## Transaction History

`tests/test_history.py`

Seed history with at least one sent ILS transaction and no GBP transactions. The page size is 20 transactions.

### HIS-01  ·  First-page row count

`test_firstPageShowsExpectedTransactionCount`

Read the total transaction count. The number of visible rows equals the smaller of 20 and the total.

### HIS-02  ·  Page navigation

`test_canNavigateBetweenTransactionPages`

With more than 20 transactions, advance to the last page and go back one page. Check page numbers, row counts, the total count, and Next and Previous states. With up to 20 transactions, verify there is no next page.

### HIS-03  ·  Filter with no matches

`test_NoMatchingTransactions`

Select GBP. The no-matching-transactions state appears. Select Clear and verify the total count and first-page rows are restored.

### HIS-04  ·  Filter by type and currency

`test_historyFiltersByTypeAndCurrency`

Select Sent and check the visible rows. Add the ILS filter. At least one row remains, and all visible rows are sent transactions with ILS amounts.

### HIS-05  ·  Open and close transaction details

`test_historyOpensAndClosesTransactionDetails`

Open the first row. Its title and amount appear in the details panel. Close the panel and verify the row is visible again.

### HIS-06  ·  Reset filter labels

`test_historyClearResetsFilterLabels`

Select GBP and then Clear. The count and rows are restored and filters return to their defaults. The test records an XFail if the results are restored but the GBP label remains.

## Notifications and Transfers

`tests/test_notifications.py`

Transfer cases are in test_sendMoney.py. Use dedicated sender and recipient accounts and an ILS wallet.

### NTF-01  ·  Unread badge count

`test_unreadBadgeMatchesNotificationList`

Compare the unread badge count with the number of unread notification rows. The counts match.

### NTF-02  ·  Filter notifications

`test_allAndUnreadFiltersShowMatchingNotifications`

Record the total and unread counts in All. Unread shows only unread notifications. Returning to All restores both counts.

### NTF-03  ·  Mark all notifications as read

`test_markAllAsReadHidesUnreadBadge`

If unread notifications exist, select Mark all as read. The badge disappears and no unread rows remain. The test skips when there are no unread notifications.

### SND-01  ·  Unknown recipient

`test_sendMoneyRejectsUnknownRecipient`

Search for a test email address on example.invalid. A rejection message appears and the Continue button is hidden.

### SND-02  ·  Zero transfer amount

`test_transferQuoteRejectsInvalidAmount[zero-agorot]`

Request a transfer quote of zero agorot for an existing recipient. The API returns HTTP 400 and INVALID_AMOUNT. The balance and transaction count are unchanged when checked after rejection.

### SND-03  ·  Negative transfer amount

`test_transferQuoteRejectsInvalidAmount[negative-agora]`

Request a transfer quote of minus one agora for an existing recipient. The API returns HTTP 400 and INVALID_AMOUNT. The balance and transaction count are unchanged when checked after rejection.

### SND-04  ·  Transfer ILS 10

`test_apiTransferAppearsInHistory`

Send ILS 10 through the API and verify a transaction ID is returned. After reload, the count increases by one and the first row shows the recipient's name, the Sent label, and the ILS 10 amount. The transaction persists.

## Settings and Display Name Validation

`tests/test_settings.py`

Sign in and open Profile & Settings. The input-validation cases intercept and block write requests. The test report includes step screenshots.

### SET-01  ·  Currency change button

`test_changeButtonRequiresDifferentCurrency`

Verify Change is disabled for the original currency, clickable after selecting a different currency, and disabled again after reselecting the original.

### SET-02  ·  Display name save button

`test_saveButtonRequiresDifferentDisplayName`

Verify Save is initially disabled, becomes clickable after editing the name, and is disabled again after restoring the original value.

### SET-03  ·  Empty display name

`test_displayNameRejectsInvalidLength[empty]`

Clear the name field and select Save. The minimum length error specifies two characters. The original name appears after reload.

### SET-04  ·  One character after trimming

`test_displayNameRejectsInvalidLength[one-character-after-trimming]`

Enter A with a space on either side and select Save. The minimum length error specifies two characters. The original name appears after reload.

### SET-05  ·  Above the maximum length

`test_displayNameRejectsInvalidLength[above-maximum]`

Enter 51 A characters and select Save. The maximum length error specifies 50 characters. The original name appears after reload.

## Saving the Display Name

`tests/test_settings.py`

Sign in and open Profile & Settings. Use test values that differ from the original display name.

### SET-06  ·  Persistence and restoration

`test_displayNamePersistsAfterReload`

Save a test name. Verify it in the profile and input field before and after reloading. Restore the original name in a finally block and verify it after another reload.

### SET-07  ·  Name containing digits

`test_validDisplayNameReachesSaveRequest[digits]`

Enter 12 and select Save. Verify that the browser issues a write request containing the value and that the test blocks it. The original name appears after reopening the settings page.

### SET-08  ·  Name containing symbols

`test_validDisplayNameReachesSaveRequest[symbols]`

Enter !@ and select Save. Verify that the browser issues a write request containing the value and that the test blocks it. The original name appears after reopening the settings page.

### SET-09  ·  Name at the maximum length

`test_validDisplayNameReachesSaveRequest[maximum]`

Enter 50 characters and select Save. Verify that the browser issues a write request containing the value and that the test blocks it. The original name appears after reopening the settings page.
