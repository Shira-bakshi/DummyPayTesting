# DummyPayTesting

Automated tests for DummyPay. The suite combines browser UI checks with Supabase API calls to verify money transfers and their appearance in transaction history.

## Test Documents and Results

- [Software Test Plan (STP)](docs/STP.md)
- [Software Test Description (STD)](docs/STD.md)
- [Full HTML test report](reports/test-report.html). Browse all modules, filter by outcome, and inspect logs and screenshots. The report is available in the `test-output` CI artifact.
- [Firefox and WebKit smoke report](reports/cross-browser-smoke.html). Available locally after a cross-browser smoke run.

The November 26, 2026 run used Chromium on Windows with Python 3.15. Of the 29 cases, 26 passed, 2 were skipped, and 1 was recorded as an expected failure (XFail). Password reset is marked Skip. The mark-as-read case skipped because there were no unread notifications. The history filter case recorded an XFail because the GBP label remained selected after clearing the filters.

One browser collects 29 cases across six modules. There are 5 `smoke` and 24 `regression` cases, including parameterized inputs.

| Module | Cases | Coverage |
| --- | ---: | --- |
| `test_login.py` | 3 | Valid and invalid sign-in, password reset navigation (marked Skip) |
| `test_dashboard.py` | 4 | Total balance in the display currency, links to Send Money, history, and notifications |
| `test_history.py` | 6 | Pagination, type and currency filters, empty state, details, and filter reset |
| `test_notifications.py` | 3 | Unread badge count, filters, and marking all notifications as read |
| `test_sendMoney.py` | 4 | Unknown recipient, invalid transfer quote amounts, and transfer visibility in history |
| `test_settings.py` | 9 | Change and Save button states, display-name validation, save requests, and persistence after reload |

## Technologies

| Component | Purpose |
| --- | --- |
| Python 3.14 | CI runtime |
| Playwright 1.64.1 | Browser automation via the sync API, screenshots, video, and traces |
| pytest 9.2.0 and pytest-playwright 0.10.0 | Discovery, execution, fixtures, and browser selection |
| pytest-html 4.2.0 | HTML reports with results and step screenshots from the settings tests |
| requests and python-dotenv | HTTP requests and loading settings from `.env` |
| Supabase and Vercel | Authentication, REST/RPC, and hosting for the DummyPay UI |
| GitHub Actions | Automated execution and upload of reports and failure artifacts |

## Browsers and Operating Systems

| Operating system | Browser | Project status |
| --- | --- | --- |
| Ubuntu Linux (`ubuntu-latest`) | Chromium | Configured in GitHub Actions |
| Windows | Chromium | Full suite run locally. See the full report |
| Windows | Firefox and WebKit | All five smoke tests passed in each engine. Regression coverage remains unverified |
| Linux and macOS | Firefox and WebKit | Available in Playwright subject to system requirements. Project compatibility remains unverified |
| Windows, Linux, and macOS | Google Chrome and Microsoft Edge | Playwright channels are available for installed browsers. Project compatibility remains unverified |

WebKit provides engine coverage relevant to Safari. See the official Playwright documentation for supported operating systems and browser channels. [System requirements](https://playwright.dev/python/docs/intro#system-requirements) · [Browsers](https://playwright.dev/python/docs/browsers)

## Installation and Configuration

From the repository root, make sure Python 3.14 is on your PATH, then create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS, activate it with `source .venv/bin/activate`. Install the dependencies and Chromium.

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium
```

On Linux, you can also install browser system dependencies with `python -m playwright install --with-deps chromium`.

Create a `.env` file in the repository root with values for the test environment.

```dotenv
TEST_USER_EMAIL=
TEST_USER_PASSWORD=
SUPABASE_ANON_KEY=
TEST_RECIPIENT_EMAIL=
TEST_RECIPIENT_NAME=
```

The API module requires the first three variables at import time, even for `--collect-only`. Use an anon or publishable Supabase key. The transfer test requires the recipient email and exact display name. The application and API URLs are defined in `utilities/consts.py` and `utilities/backend/backendBase.py`. Git ignores `.env`.

Prepare a dedicated sender with an ILS wallet holding at least ILS 10, an existing recipient, and transaction history with at least one sent ILS transaction and no GBP transactions. Seed more than 20 transactions to exercise navigation between pages. The mark-as-read test requires an unread notification. A full run sends ILS 10 to the test recipient and may mark notifications as read. The display-name persistence test attempts to restore the original name in a `finally` block. Run tests serially when they share an account.

## Running Tests and Generating Reports

```sh
python -m pytest --collect-only -q -o addopts=
python -m pytest -m smoke
python -m pytest -m regression
python -m pytest tests/test_settings.py --headed
python -m pytest --strict-markers --browser chromium --html=reports/test-report.html --self-contained-html
```

The last command runs all modules and writes the standalone HTML report. Settings in `pytest.ini` retain failure screenshots, traces, and video under `test-results/`. To open a trace locally, run `python -m playwright show-trace PATH_TO_TRACE_ZIP`.

Generate the optional settings-only report to view step screenshots. The existing presentation report generator uses Hebrew labels.

```sh
python -m pytest tests/test_settings.py --html=reports/settings-pytest.html --self-contained-html
python scripts/buildSettingsReport.py reports/settings-pytest.html reports/settings-report.html
```

To run smoke tests in Firefox and WebKit, install both engines and select them in pytest.

```sh
python -m playwright install firefox webkit
python -m pytest -m smoke --browser firefox --browser webkit --html=reports/cross-browser-smoke.html --self-contained-html
```

## Repository Structure

- `tests/` contains the six test modules.
- `pages/` contains Page Objects for UI actions and assertions.
- `utilities/backend/` contains sign-in, authenticated browser state, REST/RPC calls, and transfer helpers.
- `conftest.py` and `pytest.ini` contain fixtures, markers, and run defaults.
- `scripts/` contains the settings report generator.
- `docs/` contains the test documents. `reports/` contains locally generated HTML reports.

## GitHub Actions

The workflow in `.github/workflows/ci.yml` runs on pushes to `main`, pull requests from the same repository, and manual dispatch. The job excludes Dependabot. Define the five configuration variables as secrets in `myEnvironment`. Download `test-output` from the workflow run in the Actions tab. Reports and screenshots may contain test account information, so Git ignores `reports/`.
