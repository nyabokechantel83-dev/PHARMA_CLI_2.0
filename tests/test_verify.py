"""
Tests for utils/verify.py — the two "smart" checks in the system:
1. Is a cited prescription reference actually good?
2. Is a customer buying the same OTC(over the counter) category too often?

summary for verify_prescription():
- Reference doesn't exist            -> "not_found"
- Reference exists but expired       -> "expired"
- Reference exists but already used  -> "already_used"
- Reference exists, fresh, unused    -> "verified"

summary for otc_advisory():
- Under the threshold -> no advisory
- At/over the threshold -> an advisory message is returned
"""

from models.prescription import issue_prescription
from models.drug import add_drug
from models.order import place_order
from utils.verify import verify_prescription, otc_advisory


def test_verify_prescription_returns_not_found_for_a_fake_ref():
    status = verify_prescription(ref="RX-FAKE-000", drug_name="Amoxicillin")

    assert status == "not_found"


def test_verify_prescription_returns_expired_for_an_old_prescription(doctor):
    prescription = issue_prescription(
        doctor=doctor,
        patient_name="Josephine Njuguna",
        drug_name="Amoxicillin",
        expires_at="2026-01-01", 
    )

    status = verify_prescription(ref=prescription.ref, drug_name="Amoxicillin")

    assert status == "expired"


def test_verify_prescription_returns_verified_for_a_good_prescription(doctor):
    prescription = issue_prescription(
        doctor=doctor,
        patient_name="Josephine Njuguna",
        drug_name="Amoxicillin",
        expires_at="2030-01-01", 
    )

    status = verify_prescription(ref=prescription.ref, drug_name="Amoxicillin")

    assert status == "verified"


def test_verify_prescription_returns_already_used_after_approval(doctor):
    prescription = issue_prescription(
        doctor=doctor,
        patient_name="Josephine Njuguna",
        drug_name="Amoxicillin",
        expires_at="2030-01-01",
    )
    prescription.used = True  

    status = verify_prescription(ref=prescription.ref, drug_name="Amoxicillin")

    assert status == "already_used"


def test_otc_advisory_is_silent_under_the_threshold(customer):
    drug = add_drug(name="Panadol", price=50, stock=20, requires_prescription=False, category="analgesic")

    place_order(customer=customer, drug_id=drug.id)  

    message = otc_advisory(customer_id=customer.id, category="analgesic")

    assert message is None


def test_otc_advisory_fires_after_repeated_purchases(customer):
    drug = add_drug(name="Panadol", price=50, stock=20, requires_prescription=False, category="analgesic")

    
    place_order(customer=customer, drug_id=drug.id)
    place_order(customer=customer, drug_id=drug.id)
    place_order(customer=customer, drug_id=drug.id)

    message = otc_advisory(customer_id=customer.id, category="analgesic")

    assert message is not None