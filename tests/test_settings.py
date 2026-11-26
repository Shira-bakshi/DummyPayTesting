from base64 import b64encode
from pathlib import Path

import pytest
from playwright.sync_api import expect
from pytest_html import extras as htmlExtras

from utilities.consts import CURRENCY


@pytest.fixture
def captureStep(settings, request, pytestconfig, extras):
    directory = Path(pytestconfig.getoption("--output")) / "settings-steps" / request.node.name
    directory.mkdir(parents=True, exist_ok=True)

    def capture(title):
        path = directory / f"{len(extras) + 1:02d}-{title}.png"
        screenshot = settings.page.screenshot(path=path, full_page=True)
        extras.append(htmlExtras.png(b64encode(screenshot).decode("ascii"), name=path.stem))

    return capture


@pytest.mark.regression
def test_changeButtonRequiresDifferentCurrency(settings, captureStep):
    originalCurrency = settings.getPreferredCurrency()
    newCurrency = next(currency for currency in CURRENCY if currency != originalCurrency)

    settings.expectSelectedCurrency(originalCurrency)
    settings.expectCurrencyChangeDisabled()
    captureStep("original-currency-change-disabled")

    settings.selectCurrency(newCurrency)
    settings.expectCurrencyChangeClickable()
    captureStep("different-currency-change-enabled")

    settings.selectCurrency(originalCurrency)
    settings.expectCurrencyChangeDisabled()
    captureStep("original-currency-restored")


@pytest.fixture
def displayNameSettings(settings):
    def blockWrites(route):
        if route.request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            route.abort()
        else:
            route.continue_()

    settings.page.route("**/*", blockWrites)
    return settings


@pytest.mark.regression
def test_saveButtonRequiresDifferentDisplayName(displayNameSettings, captureStep):
    settings = displayNameSettings
    originalName = settings.getDisplayName()
    newName = "QA name" if originalName != "QA name" else "QA display name"

    settings.expectDisplayNameSaveDisabled()
    captureStep("original-name-save-disabled")
    settings.fillDisplayName(newName)
    settings.expectDisplayNameSaveClickable()
    captureStep("different-name-save-enabled")
    settings.fillDisplayName(originalName)
    settings.expectDisplayNameSaveDisabled()
    captureStep("original-name-restored")


@pytest.mark.regression
@pytest.mark.parametrize(
    ("name", "message"),
    [
        ("", "Display name must be at least 2 characters."),
        (" A ", "Display name must be at least 2 characters."),
        ("A" * 51, "Display name must be at most 50 characters."),
    ],
    ids=["empty", "one-character-after-trimming", "above-maximum"],
)
def test_displayNameRejectsInvalidLength(displayNameSettings, name, message, captureStep):
    originalName = displayNameSettings.getDisplayName()
    captureStep("original-display-name")
    displayNameSettings.fillDisplayName(name)
    captureStep("invalid-name-before-save")
    displayNameSettings.saveDisplayName()
    displayNameSettings.expectDisplayNameError(message)
    captureStep("validation-error-after-save")
    displayNameSettings.page.reload()
    displayNameSettings.expectSavedDisplayName(originalName)
    captureStep("original-name-after-reload")


@pytest.mark.regression
def test_displayNamePersistsAfterReload(settings, captureStep):
    originalName = settings.getDisplayName()
    newName = "QA Tester" if originalName != "QA Tester" else "QA Reviewer"
    captureStep("original-display-name")

    try:
        settings.fillDisplayName(newName)
        captureStep("new-name-before-save")
        settings.saveDisplayName()
        settings.expectSavedDisplayName(newName)
        captureStep("new-name-after-save")

        settings.page.reload()
        settings.expectSavedDisplayName(newName)
        captureStep("new-name-after-reload")
    finally:
        settings.open()
        if settings.getDisplayName() != originalName:
            settings.fillDisplayName(originalName)
            settings.saveDisplayName()
            settings.expectSavedDisplayName(originalName)

        settings.page.reload()
        settings.expectSavedDisplayName(originalName)
        captureStep("original-name-restored-after-reload")


@pytest.mark.regression
@pytest.mark.parametrize("name", ["12", "!@", "A" * 50], ids=["digits", "symbols", "maximum"])
def test_validDisplayNameReachesSaveRequest(displayNameSettings, name, captureStep):
    settings = displayNameSettings
    originalName = settings.getDisplayName()
    if name == originalName:
        name = name[::-1] if name != "A" * 50 else "B" * 50

    captureStep("original-display-name")
    settings.fillDisplayName(name)
    captureStep("valid-name-before-save")
    with settings.page.expect_event(
        "requestfailed",
        lambda request: request.method in {"POST", "PUT", "PATCH"}
        and name in (request.post_data or "")
    ):
        settings.saveDisplayName()
    settings.expectDisplayNameSaveClickable()
    captureStep("after-save-request-blocked")

    settings.open()
    expect(settings.displayNameField).to_have_value(originalName)
    captureStep("original-name-after-reopening")
