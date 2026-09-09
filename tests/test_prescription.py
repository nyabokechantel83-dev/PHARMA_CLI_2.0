"""
Tests for models/prescription.py — prescriptions issued by a doctor.

Plain-English summary:
- Only a doctor can issue a prescription (this is what stops a
  customer from just making up a fake reference number).
- A newly issued prescription starts out "not used".
- We can look a prescription up later by its reference code.
"""

import pytest

from models.prescription import issue_prescription, get_prescription


def test_issue_prescription_creates_a_record(doctor):
    prescription = issue_prescription(
        doctor=doctor,
        patient_name="John Maina",
        drug_name="Amoxicillin",
        expires_at="2026-12-31",
    )

    assert prescription.patient_name == "John Maina"
    assert prescription.drug_name == "Amoxicillin"
    assert prescription.doctor_id == doctor.id


def test_new_prescription_starts_as_unused(doctor):
    prescription = issue_prescription(
        doctor=doctor,
        patient_name="John Maina",
        drug_name="Amoxicillin",
        expires_at="2026-12-31",
    )

    assert prescription.used is False


def test_only_a_doctor_can_issue_a_prescription(customer):
    with pytest.raises(Exception):
        issue_prescription(
            doctor=customer,
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31",
        )


def test_get_prescription_finds_it_by_ref(doctor):
    prescription = issue_prescription(
        doctor=doctor,
        patient_name="John Maina",
        drug_name="Amoxicillin",
        expires_at="2026-12-31",
    )

    found = get_prescription(prescription.ref)

    assert found.ref == prescription.ref


def test_get_prescription_returns_none_for_an_unknown_ref():
    assert get_prescription("RX-DOES-NOT-EXIST") is None
