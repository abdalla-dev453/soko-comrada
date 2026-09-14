"""Safaricom Daraja STK Push integration (Phase 5 roadmap item).

Replaces "type in the M-Pesa code, wait for an admin" with a phone
prompt the student confirms with their PIN — Safaricom's callback
verifies the payment automatically.

Requires real Daraja credentials to actually reach Safaricom (see
DARAJA_* env vars in .env.example) and a publicly reachable callback
URL (ngrok or similar in dev, since Safaricom must be able to POST
back to DARAJA_CALLBACK_URL). Falls back to raising DarajaError with
a clear message if credentials are missing, so the route layer can
degrade to the manual-code flow rather than crash.

Manual verification (payment_service.submit_payment) is NOT removed —
it stays as the fallback path when a callback never arrives (network
blip, user closed the STK prompt) or during local development without
Daraja sandbox access.
"""

import base64
from datetime import datetime, timezone

import requests

DARAJA_ENV_SANDBOX = "sandbox"
DARAJA_ENV_PRODUCTION = "production"

_BASE_URLS = {
    DARAJA_ENV_SANDBOX: "https://sandbox.safaricom.co.ke",
    DARAJA_ENV_PRODUCTION: "https://api.safaricom.co.ke",
}


class DarajaError(Exception):
    """Raised for expected, user-facing STK Push failures — missing
    config, Daraja rejecting the request, a phone number Safaricom
    won't prompt. Routes translate these into 4xx JSON responses and
    can offer the manual-code flow as a fallback."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _base_url(app_config) -> str:
    env = app_config.get("DARAJA_ENV", DARAJA_ENV_SANDBOX)
    return _BASE_URLS.get(env, _BASE_URLS[DARAJA_ENV_SANDBOX])


def _require_config(app_config, *keys) -> None:
    missing = [k for k in keys if not app_config.get(k)]
    if missing:
        raise DarajaError(
            "STK Push isn't configured yet ("
            + ", ".join(missing)
            + " missing) — use the manual M-Pesa code option instead.",
            status_code=503,
        )


def get_access_token(app_config) -> str:
    _require_config(app_config, "DARAJA_CONSUMER_KEY", "DARAJA_CONSUMER_SECRET")

    auth = (app_config["DARAJA_CONSUMER_KEY"], app_config["DARAJA_CONSUMER_SECRET"])
    url = f"{_base_url(app_config)}/oauth/v1/generate?grant_type=client_credentials"

    try:
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DarajaError(f"Couldn't reach Safaricom to authenticate: {exc}") from exc

    token = response.json().get("access_token")
    if not token:
        raise DarajaError("Safaricom didn't return an access token.")
    return token


def _password(app_config, timestamp: str) -> str:
    shortcode = app_config["DARAJA_SHORTCODE"]
    passkey = app_config["DARAJA_PASSKEY"]
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode("utf-8")).decode("utf-8")


def initiate_stk_push(
    app_config, *, phone_number: str, amount: int, account_reference: str, description: str
) -> dict:
    """Kicks off an STK Push prompt on the payer's phone.

    Returns Daraja's response dict, which includes CheckoutRequestID
    (the correlation id the callback will echo back) and
    MerchantRequestID. Raises DarajaError on any failure.
    """
    _require_config(
        app_config, "DARAJA_SHORTCODE", "DARAJA_PASSKEY", "DARAJA_CALLBACK_URL"
    )

    token = get_access_token(app_config)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    shortcode = app_config["DARAJA_SHORTCODE"]

    payload = {
        "BusinessShortCode": shortcode,
        "Password": _password(app_config, timestamp),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": app_config["DARAJA_CALLBACK_URL"],
        "AccountReference": account_reference[:12],
        "TransactionDesc": description[:13],
    }

    url = f"{_base_url(app_config)}/mpesa/stkpush/v1/processrequest"
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DarajaError(f"Safaricom rejected the STK Push request: {exc}") from exc

    data = response.json()
    if data.get("ResponseCode") != "0":
        raise DarajaError(data.get("ResponseDescription", "STK Push request failed."))

    return data


def parse_callback(payload: dict) -> dict:
    """Parses the POST body Safaricom sends to DARAJA_CALLBACK_URL.

    Returns a normalized dict with checkout_request_id, success,
    mpesa_receipt, amount, and phone_number (the latter three only
    populated on success). Raises DarajaError if the payload doesn't
    look like a Daraja callback at all — this endpoint has no auth,
    so it must tolerate garbage input without crashing.
    """
    try:
        stk_callback = payload["Body"]["stkCallback"]
        checkout_request_id = stk_callback["CheckoutRequestID"]
        result_code = stk_callback["ResultCode"]
    except (KeyError, TypeError) as exc:
        raise DarajaError("Malformed Daraja callback payload.", status_code=400) from exc

    success = result_code == 0
    result = {
        "checkout_request_id": checkout_request_id,
        "success": success,
        "mpesa_receipt": None,
        "amount": None,
        "phone_number": None,
    }

    if not success:
        return result

    items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
    values = {item.get("Name"): item.get("Value") for item in items}
    result["mpesa_receipt"] = values.get("MpesaReceiptNumber")
    result["amount"] = values.get("Amount")
    result["phone_number"] = str(values.get("PhoneNumber", "")) or None
    return result
