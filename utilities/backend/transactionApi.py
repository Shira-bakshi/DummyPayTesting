import os
import uuid

from utilities.backend.backendBase import rpc
from utilities.consts import  Functions


__all__ = ["sendFunds"]

def sendFunds(userMail, amount , currency):
    recipient = rpc(Functions.LOOKUP_RECEPIENT, {"p_email": userMail})
    quote = rpc(Functions.CREATE_TRANSFER_QUOTE, {
        "p_recipient_id": recipient[0].get("user_id"),   # check the exact return shape
        "p_sending_currency": currency,         # ILS | USD | EUR | GBP
        "p_amount_minor": amount,              # 10.00
        "p_input_side": "send",              # send | receive
    })
    response = rpc("execute_transfer", {
        "p_quote_id": quote.get("quote_id"),
        "p_idempotency_key": str(uuid.uuid4()),
    })
    return response

# if __name__ == "__main__":
#     print(send_funds(user_mail=os.environ["TEST_RECIPIENT_EMAIL"]))