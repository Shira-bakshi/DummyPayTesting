from enum import StrEnum


FILE_PATH = "https://dummypay.vercel.app/"

CONSTS: dict[str, str] = {
    "alertMessage": "Incorrect email or password."
}

class CURRENCY(StrEnum):
    USD = 'USD'
    ILS = 'ILS'
    GBP = 'GBP'
    EUR = 'EUR'


class Tables(StrEnum):
    WALLETS = 'wallets'

class Functions(StrEnum):
    LOOKUP_RECEPIENT = "lookup_recipient"
    CREATE_TRANSFER_QUOTE = "create_transfer_quote"
    WALLET_SUMMARY = "get_wallet_summary"
