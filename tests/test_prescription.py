
import pytest  # type: ignore[import-not-found]

from models.prescription import issue_prescription, get_prescription


class TestPrescription:

    def test_issue_prescription_creates_a_record(self, doctor_user):
        prescription = issue_prescription(
            doctor=doctor_user,
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31",
        )

        assert prescription.patient_name == "John Maina"
        assert prescription.drug_name == "Amoxicillin"
        assert prescription.doctor_id == doctor_user.id

    def test_new_prescription_starts_as_unused(self, doctor_user):
        prescription = issue_prescription(
            doctor=doctor_user,
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31",
        )

        assert prescription.used is False

class TestIssuePrescription:
    def test_only_a_doctor_can_issue_a_prescription(self, customer_user):
        with pytest.raises(Exception):
            issue_prescription(
                doctor=customer_user,
                patient_name="John Maina",
                drug_name="Amoxicillin",
                expires_at="2026-12-31",
            )

class TestGetPrescription:
    def test_get_prescription_finds_it_by_ref(self, doctor_user):
        prescription = issue_prescription(
            doctor=doctor_user,
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31",
        )
        found = get_prescription(prescription.ref)
        assert found.ref == prescription.ref

    def test_get_prescription_returns_none_for_an_unknown_ref(self):
        assert get_prescription("RX-DOES-NOT-EXIST") is None