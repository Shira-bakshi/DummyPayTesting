# DummyPay Software Test Plan

*STP  |  Version 1.0  |  November 26, 2026*

This plan defines how to run and evaluate the DummyPay automation suite. It guides developers and testers in verifying changes to the interface, account settings, and money transfer flow.

## Objectives and Scope

Login and dashboard coverage includes valid and invalid sign-in, conversion of wallet balances to the display currency, and navigation to key features.

History and notification coverage includes pagination, filters, transaction details, the unread count, and marking notifications as read.

Transfer and settings coverage includes recipient lookup, API rejection of invalid transfer amounts, transfers in history, display-name validation and persistence, and availability of the currency change button.

The current suite excludes performance, security, accessibility, mobile testing, completing a transfer through the UI, and saving the display currency. The password reset navigation test is marked Skip.

## Test Strategy

Smoke tests cover sign-in and key navigation links. Regression tests cover functional behavior, invalid inputs, boundary values, and API-to-UI integration. One browser collects 29 cases, including 5 Smoke and 24 Regression cases. One Regression case is always skipped.

Page Objects encapsulate navigation, locators, and UI assertions. Fixtures sign in through Supabase and load storage state into an authenticated browser context. The sign-in tests exercise the UI form directly.

## Technologies

CI uses Python 3.14. The suite uses the Playwright 1.64.1 sync API, pytest 9.2.0, pytest-playwright 0.10.0, and pytest-html 4.2.0. The requests library makes HTTP calls, and python-dotenv loads environment variables.

The suite tests the interface deployed on Vercel. Supabase provides authentication, REST access, and RPCs. GitHub Actions generates the HTML report and uploads test artifacts.

## Test Environments and Exit Criteria

### Browser and Operating System Matrix

Ubuntu Linux with Chromium is configured in GitHub Actions on ubuntu-latest. Use the CI report to verify the result of a particular run.

The full suite ran locally on Windows with Chromium and Python 3.15. Of 29 cases, 26 passed, 2 were skipped, and 1 was classified as XFail. See the HTML report for details.

All five Smoke tests passed in both Firefox and WebKit on Windows. Regression coverage for both engines and project compatibility on Linux or macOS with those engines remain unverified.

Playwright can use installed Chrome and Edge channels. WebKit provides engine coverage relevant to Safari. The README links to system requirements and browser channel documentation.

### Entry Criteria and Test Data

Install the project dependencies and browser, verify access to the application and Supabase, and configure the five variables listed in the README. The sender needs an ILS wallet with at least ILS 10 available. The recipient's display name must match the configured value.

Seed history with at least one sent ILS transaction and no GBP transactions. More than 20 transactions are needed to exercise navigation between pages. The mark-as-read test requires at least one unread notification.

Run the suite serially with a dedicated test account. The transfer test creates a persistent transaction and changes balances. Marking notifications as read persists. The display-name persistence test restores the original name in a finally block. Reset test data as needed before rerunning.

### Test Artifacts and Exit Criteria

Run Smoke for a focused check. For full regression, run the entire suite and retain the pytest-html report. Review screenshots, video, and traces when available for failures.

A run is ready for sign-off when all active tests pass and every Skip or XFail has a documented reason. Record setup errors separately from functional failures. After a fix, rerun the affected scenario and test group.

Clearing history filters can restore the transaction results while leaving the GBP label selected. The relevant test classifies that specific outcome as XFail.
