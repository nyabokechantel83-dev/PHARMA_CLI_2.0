from datetime import date, timedelta

from models import order as order_model
from models import prescription as prescription_model


VERIFIED = "verified"
NOT_FOUND = "not_found"
DRUG_MISMATCH = "drug_mismatch"
NAME_MISMATCH = "name_mismatch"
EXPIRED = "expired"
ALREADY_USED = "already_used"
NOT_REQUIRED = "not_required"


VERIFICATION_MESSAGES = {
    VERIFIED: "Verified - prescription is valid and unused",
    NOT_FOUND: "NOT FOUND - no prescription with this reference exists",
    DRUG_MISMATCH: "MISMATCH - the prescription is for a different drug",
    NAME_MISMATCH: "MISMATCH - the prescription was issued to a different patient",
    EXPIRED: "EXPIRED - the prescription is past its expiry date",
    ALREADY_USED: "ALREADY USED - this prescription was used on an earlier order",
    NOT_REQUIRED: "Not required - this drug is sold over the counter",
}

ADVISORY_DAYS = 30
ADVISORY_LIMIT = 3


def describe(verification_status):
    return VERIFICATION_MESSAGES.get(verification_status, verification_status)


def check_prescription(ref, drug, customer, today=None):
    if today is None:
        today = date.today()

    found = prescription_model.find_by_ref(ref)

    if found is None:
        return NOT_FOUND

    if found.drug_name.lower() != drug.name.lower():
        return DRUG_MISMATCH

    if found.patient_name.lower() != customer.name.lower():
        return NAME_MISMATCH

    if date.fromisoformat(found.expires_at) < today:
        return EXPIRED

    if found.used:
        return ALREADY_USED

    return VERIFIED


def otc_advisory(customer, drug, today=None):
    if today is None:
        today = date.today()

    if drug.requires_rx:
        return None

    window_starts = today - timedelta(days=ADVISORY_DAYS)
    recent_count = 0

    for past_order in order_model.orders_for_customer(customer.id):
        if past_order.drug_id != drug.id:
            continue

        if past_order.status == order_model.STATUS_REJECTED:
            continue

        if date.fromisoformat(past_order.created_at) >= window_starts:
            recent_count += 1
    purchases_including_this_one = recent_count + 1

    if purchases_including_this_one < ADVISORY_LIMIT:
        return None

    return (
        f"ADVISORY: {customer.name} has bought {drug.name} "
        f"{purchases_including_this_one} times in the last {ADVISORY_DAYS} days."
    )
