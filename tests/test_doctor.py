from types import SimpleNamespace
from datetime import date, timedelta
import pytest  # type: ignore[reportMissingImports]
from cli.doctor import issue_prescription, list_prescriptions

class TestIssuePrescription:
    def test_doctor_can_issue_prescription(self, monkeypatch, capsys):
        doctor = SimpleNamespace(id=1, role="doctor")
        args = SimpleNamespace(patient_name="John Maina", drug_name="Amoxicillin", days_valid=30)
        saved = {}

        monkeypatch.setattr("cli.doctor.prescription_model.load_prescriptions", lambda: [])
        monkeypatch.setattr("cli.doctor.prescription_model.save_prescriptions", lambda rows: saved.setdefault("rows", rows))
        monkeypatch.setattr("cli.doctor.prescription_model.make_ref", lambda rows: "RX-0001")

        issue_prescription.__wrapped__(args, doctor)

        prescriptions = saved["rows"]

        output = capsys.readouterr().out

        assert len(prescriptions) == 1
        assert prescriptions[0].ref == "RX-0001"
        assert prescriptions[0].patient_name == "John Maina"
        assert prescriptions[0].doctor_id == 1
        assert prescriptions[0].drug_name == "Amoxicillin"
        assert prescriptions[0].used is False
        assert prescriptions[0].date_issued == date.today().isoformat()
        assert prescriptions[0].expires_at == (date.today() + timedelta(days=30)).isoformat()
        assert "Prescription created: RX-0001" in output

    def test_invalid_days_valid_raises_error(self):
        doctor = SimpleNamespace(id=1, role="doctor")
        args = SimpleNamespace(patient_name="John Maina", drug_name="Amoxicillin", days_valid=0)

        with pytest.raises(ValueError):
            issue_prescription.__wrapped__(args, doctor)

class TestListPrescriptions:
    def test_list_prescriptions_for_current_doctor(self, monkeypatch, capsys):
        doctor = SimpleNamespace(id=1, role="doctor")
        prescriptions = [
            SimpleNamespace(ref="RX-0001", patient_name="John Maina", doctor_id=1, drug_name="Amoxicillin", expires_at="2026-12-31", used=False),
            SimpleNamespace(ref="RX-0002", patient_name="Jane Doe", doctor_id=2, drug_name="Panadol", expires_at="2026-12-31", used=False)
        ]

        monkeypatch.setattr("cli.doctor.prescription_model.load_prescriptions", lambda: prescriptions)

        args = SimpleNamespace()
        list_prescriptions.__wrapped__(args, doctor)

        output = capsys.readouterr().out

        assert "RX-0001" in output
        assert "John Maina" in output
        assert "Amoxicillin" in output
        assert "RX-0002" not in output
        assert "Jane Doe" not in output

    def test_list_prescriptions_when_none_exist(self, monkeypatch, capsys):
        doctor = SimpleNamespace(id=1, role="doctor")

        monkeypatch.setattr("cli.doctor.prescription_model.load_prescriptions", lambda: [])

        args = SimpleNamespace()
        list_prescriptions.__wrapped__(args, doctor)

        output = capsys.readouterr().out

        assert "No prescriptions found" in output