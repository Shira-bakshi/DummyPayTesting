import json
import os
import re
import pytest
from playwright.sync_api import expect
from utilities.backend.backendBase import EMAIL, PASSWORD, rpc, signIn, table
from utilities.backend.transactionApi import sendFunds
from utilities.consts import CURRENCY, FILE_PATH, Functions, Tables


@pytest.mark.regression
def test_sendMoneyRejectsUnknownRecipient(sendMoneyPage):
    sendMoneyPage.fillEmail("missing-recipient-qa@example.invalid")
    sendMoneyPage.clickFindRecipient()
    sendMoneyPage.expectUnknownRecipientRejected()


def getIlsBalanceMinor(senderId):
    wallets = table(
        Tables.WALLETS,
        {"user_id": f"eq.{senderId}", "currency": f"eq.{CURRENCY.ILS}"},
    ).json()
    assert len(wallets) == 1, "Expected one ILS wallet for the test sender"
    return wallets[0]["balance_minor"]


@pytest.mark.regression
@pytest.mark.parametrize(
        "amountMinor",
        [0, -1],
        ids=["zero-agorot", "negative-agora"])
def test_transferQuoteRejectsInvalidAmount(dashboard, amountMinor):
    recipient = rpc(
        Functions.LOOKUP_RECEPIENT,
        {"p_email": os.environ["TEST_RECIPIENT_EMAIL"]},
    )
    assert recipient and recipient[0].get("user_id"), "Test recipient must exist"
    senderId = signIn(EMAIL, PASSWORD)["user"]["id"]

    page = dashboard.page
    dashboard.openRecentTransactions()
    expect(page).to_have_url(f"{FILE_PATH}history")
    transactionCount = page.get_by_role("main").get_by_text(
        re.compile(r"^\d+ transactions?$")
    )
    expect(transactionCount).to_be_visible()
    countBefore = transactionCount.inner_text()
    balanceBefore = getIlsBalanceMinor(senderId)

    with pytest.raises(RuntimeError) as error:
        rpc(
            Functions.CREATE_TRANSFER_QUOTE,
            {
                "p_recipient_id": recipient[0]["user_id"],
                "p_sending_currency": CURRENCY.ILS,
                "p_amount_minor": amountMinor,
                "p_input_side": "send",
            },
        )

    operation, response = str(error.value).split(": ", 1)
    status, body = response.split(" ", 1)
    assert operation == Functions.CREATE_TRANSFER_QUOTE
    assert status == "400"
    reason = json.loads(body)["message"].partition(":")[0]
    assert reason == "INVALID_AMOUNT"
    print(f"\nAPI rejected {amountMinor} agorot: HTTP {status} {reason}")

    balanceAfter = getIlsBalanceMinor(senderId)
    assert balanceAfter == balanceBefore, "Sender balance changed after rejection"
    page.reload()
    expect(transactionCount).to_have_text(countBefore)


@pytest.mark.regression
def test_apiTransferAppearsInHistory(dashboard):
    recipientEmail = os.getenv("TEST_RECIPIENT_EMAIL")
    if not recipientEmail:
        pytest.fail("Set TEST_RECIPIENT_EMAIL to a test account in .env")

    recipientName = os.getenv("TEST_RECIPIENT_NAME", "shira bakshi")
    amountIls = 10
    page = dashboard.page
    historyUrl = f"{FILE_PATH}history"
    history = page.get_by_role("main")
    transactionCount = history.get_by_text(re.compile(r"^\d+ transactions?$"))

    dashboard.openRecentTransactions()
    expect(page).to_have_url(historyUrl)
    expect(transactionCount).to_be_visible()
    countBefore = int(transactionCount.inner_text().split()[0])

    transaction = sendFunds(
        userMail=recipientEmail,
        amount=amountIls * 100,  # The API expects agorot.
        currency=CURRENCY.ILS,
    )

    transactionId = transaction.get("transaction_id") or transaction.get("id")
    assert transactionId, "The transfer response did not include a transaction ID"

    page.reload()
    expect(transactionCount).to_have_text(f"{countBefore + 1} transactions")

    latestTransfer = history.get_by_role("listitem").first.get_by_role("button")
    amount = f"₪{amountIls:,.2f}"
    expect(latestTransfer).to_have_accessible_name(
        re.compile(rf"^To {re.escape(recipientName)} Sent\b.*{re.escape(amount)}$")
    )
