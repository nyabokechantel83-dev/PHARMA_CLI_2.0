from types import SimpleNamespace

import pytest  # type: ignore[import-not-found]

from cli.doctor import (
    _issue_prescription_for_current_doctor,
)


def assert_raises(expected_exception, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except expected_exception:
        return
    except Exception as exc:
        raise AssertionError(
            f"Expected {expected_exception.__name__}, got {type(exc).__name__}: {exc}"
        ) from exc

    raise AssertionError(
        f"Expected {expected_exception.__name__}, but no exception was raised"
    )


class TestDoctorPrescription:

    def test_doctor_can_issue_prescription(self):
        doctor = SimpleNamespace(
            id="D001",
            role="doctor"
        )

        prescription = SimpleNamespace(
            ref="RX-12345678",
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31"
        )

        prescription_service = SimpleNamespace(
            issue_prescription=lambda **kwargs: prescription
        )

        services = SimpleNamespace(
            prescription=prescription_service
        )

        args = SimpleNamespace(
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31"
        )

        _issue_prescription_for_current_doctor(
            current_doctor=doctor,
            args=args,
            services=services
        )

        assert prescription.patient_name == "John Maina"
        assert prescription.drug_name == "Amoxicillin"
        assert prescription.expires_at == "2026-12-31"

    def test_prescription_is_issued_by_current_doctor(self):
        doctor = SimpleNamespace(
            id="D001",
            role="doctor"
        )

        captured = {}

        def issue_prescription(**kwargs):
            captured.update(kwargs)

            return SimpleNamespace(
                ref="RX-12345678",
                patient_name=kwargs["patient_name"],
                drug_name=kwargs["drug_name"],
                expires_at=kwargs["expires_at"]
            )

        services = SimpleNamespace(
            prescription=SimpleNamespace(
                issue_prescription=issue_prescription
            )
        )

        args = SimpleNamespace(
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31"
        )

        _issue_prescription_for_current_doctor(
            current_doctor=doctor,
            args=args,
            services=services
        )

        assert captured["doctor"] is doctor
        assert captured["patient_name"] == "John Maina"
        assert captured["drug_name"] == "Amoxicillin"
        assert captured["expires_at"] == "2026-12-31"

    def test_non_doctor_cannot_issue_prescription(self):
        customer = SimpleNamespace(
            id="C001",
            role="customer"
        )

        services = SimpleNamespace(
            prescription=SimpleNamespace(
                issue_prescription=lambda **kwargs: None
            )
        )

        args = SimpleNamespace(
            patient_name="John Maina",
            drug_name="Amoxicillin",
            expires_at="2026-12-31"
        )

        with pytest.raises(Exception):
            _issue_prescription_for_current_doctor(
                current_doctor=customer,
                args=args,
                services=services
            )