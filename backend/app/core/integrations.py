"""Thin integration stubs for Stripe + SendGrid. In dev (no API key set) they print to stdout."""
from datetime import date
from typing import Any

from app.config import settings


# ────────────────────────────────────────────
# Stripe
# ────────────────────────────────────────────


def has_stripe() -> bool:
    return bool(settings.stripe_secret_key)


def create_payment_link(invoice_number: str, amount: float, currency: str = "usd") -> str:
    """Return a payment URL for the client to pay an invoice."""
    if not has_stripe():
        return f"[stub-stripe] Payment link for invoice {invoice_number} (${amount:.2f} {currency.upper()})"
    try:
        import stripe  # type: ignore
        stripe.api_key = settings.stripe_secret_key
        # In real life you'd create a Checkout Session and return `session.url`
        return f"https://checkout.stripe.com/c/pay/{invoice_number}"
    except Exception as e:
        return f"[stripe-error] {e}"


def mark_invoice_paid_remotely(invoice_id: str) -> dict[str, Any]:
    """Optional: query Stripe for paid status and reconcile."""
    return {"status": "no-stripe", "invoice_id": invoice_id}


# ────────────────────────────────────────────
# SendGrid
# ────────────────────────────────────────────


def has_sendgrid() -> bool:
    return bool(settings.sendgrid_api_key)


def send_email(
    to: str,
    subject: str,
    html: str,
    from_email: str | None = None,
) -> bool:
    """Send an email via SendGrid. Returns True if dispatched."""
    if not has_sendgrid():
        print(f"[stub-sendgrid] To: {to} | Subject: {subject}")
        print("---")
        print(html)
        print("---")
        return True
    try:
        from sendgrid import SendGridAPIClient  # type: ignore
        from sendgrid.helpers.mail import Mail  # type: ignore

        msg = Mail(
            from_email=from_email or settings.sendgrid_from_email,
            to_emails=to,
            subject=subject,
            html_content=html,
        )
        client = SendGridAPIClient(settings.sendgrid_api_key)
        client.send(msg)
        return True
    except Exception as e:
        print(f"[sendgrid-error] {e}")
        return False
