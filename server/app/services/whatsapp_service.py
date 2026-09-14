"""WhatsApp Business Cloud API integration (Phase 7 roadmap item).

Replaces the SMTP email fallback for the same three "critical action"
events notification_service.py already identifies (application
accepted, gig completed, payment verified) — WhatsApp open rates on
this demographic run far higher than university email.

Requires a Meta WhatsApp Business API app + approved message
templates (see WHATSAPP_* env vars). Template approval is the slow
part (can take days), not the code — this module is correct and
complete against the Cloud API's documented shape, but won't reach a
real device without real credentials and approved templates.

send_whatsapp_message never raises out to callers: a failed
notification must not fail the request that triggered it (accepting
an application should still succeed even if WhatsApp is down), same
principle as notification_service.send_critical_email.
"""

import requests

GRAPH_API_VERSION = "v20.0"


def _is_configured(app_config) -> bool:
    return bool(app_config.get("WHATSAPP_TOKEN") and app_config.get("WHATSAPP_PHONE_NUMBER_ID"))


def send_whatsapp_message(
    app_config, *, to_phone_number: str, template_name: str, template_params: list[str], logger=None
) -> bool:
    """Sends an approved WhatsApp template message.

    template_params fill the template's {{1}}, {{2}}, ... placeholders
    in order. Returns True if the API accepted the request, False if
    not configured or the request failed — never raises.
    """
    if not _is_configured(app_config):
        if logger:
            logger.info(
                "WhatsApp not configured — would send template %s to %s",
                template_name,
                to_phone_number,
            )
        return False

    phone_number_id = app_config["WHATSAPP_PHONE_NUMBER_ID"]
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone_number.lstrip("+"),
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in template_params],
                }
            ],
        },
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {app_config['WHATSAPP_TOKEN']}"},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        if logger:
            logger.exception("Failed to send WhatsApp message to %s", to_phone_number)
        return False


# --- Convenience wrappers for the three critical events ---
# Template names below must match templates approved in Meta Business
# Manager exactly — these are the names this project would register.


def notify_application_accepted(app_config, *, applicant_phone, poster_name, gig_title, logger=None):
    return send_whatsapp_message(
        app_config,
        to_phone_number=applicant_phone,
        template_name="comradeplug_application_accepted",
        template_params=[poster_name, gig_title],
        logger=logger,
    )


def notify_gig_completed(app_config, *, to_phone, gig_title, logger=None):
    return send_whatsapp_message(
        app_config,
        to_phone_number=to_phone,
        template_name="comradeplug_gig_completed",
        template_params=[gig_title],
        logger=logger,
    )


def notify_payment_verified(app_config, *, to_phone, purpose_label, logger=None):
    return send_whatsapp_message(
        app_config,
        to_phone_number=to_phone,
        template_name="comradeplug_payment_verified",
        template_params=[purpose_label],
        logger=logger,
    )
