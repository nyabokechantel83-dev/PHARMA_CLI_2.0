from types import SimpleNamespace
import models.prescription

def test_prescription_to_dict():
    prescription=models.prescription.Prescription(
        ref="RX-0001",
        patient_name="John Maina",
        doctor_id=1,
        drug_name="Amoxicillin",
        date_issued="2026-09-12",
        expires_at="2026-12-31",
        used=False
    )
    data=prescription.to_dict()
    assert data["ref"]=="RX-0001"
    assert data["patient_name"]=="John Maina"
    assert data["doctor_id"]==1
    assert data["drug_name"]=="Amoxicillin"
    assert data["date_issued"]=="2026-09-12"
    assert data["expires_at"]=="2026-12-31"
    assert data["used"] is False

def test_prescription_from_dict():
    data={
        "ref":"RX-0002",
        "patient_name":"Jane Doe",
        "doctor_id":2,
        "drug_name":"Panadol",
        "date_issued":"2026-09-12",
        "expires_at":"2026-12-31",
        "used":False
    }
    prescription=models.prescription.Prescription.from_dict(data)
    assert prescription.ref=="RX-0002"
    assert prescription.patient_name=="Jane Doe"
    assert prescription.doctor_id==2
    assert prescription.drug_name=="Panadol"
    assert prescription.used is False

def test_save_and_load_prescriptions(monkeypatch):
    data=[]
    monkeypatch.setattr("models.prescription.storage.write_json",lambda file_name,rows:data.extend(rows))
    monkeypatch.setattr("models.prescription.storage.read_json",lambda file_name:data)

    prescription=models.prescription.Prescription(
        ref="RX-0003",
        patient_name="John Maina",
        doctor_id=1,
        drug_name="Amoxicillin",
        date_issued="2026-09-12",
        expires_at="2026-12-31",
        used=False
    )

    models.prescription.save_prescriptions([prescription])
    loaded=models.prescription.load_prescriptions()

    assert len(loaded)==1
    assert loaded[0].ref=="RX-0003"
    assert loaded[0].patient_name=="John Maina"
    assert loaded[0].drug_name=="Amoxicillin"

def test_find_by_ref(monkeypatch):
    prescription=models.prescription.Prescription(
        ref="RX-0004",
        patient_name="John Maina",
        doctor_id=1,
        drug_name="Amoxicillin",
        date_issued="2026-09-12",
        expires_at="2026-12-31",
        used=False
    )

    monkeypatch.setattr("models.prescription.load_prescriptions",lambda:[prescription])

    found=models.prescription.find_by_ref("RX-0004")
    assert found is prescription

def test_find_by_ref_is_case_insensitive(monkeypatch):
    prescription=models.prescription.Prescription(
        ref="RX-0005",
        patient_name="John Maina",
        doctor_id=1,
        drug_name="Amoxicillin",
        date_issued="2026-09-12",
        expires_at="2026-12-31",
        used=False
    )

    monkeypatch.setattr("models.prescription.load_prescriptions",lambda:[prescription])

    found=models.prescription.find_by_ref("rx-0005")
    assert found is prescription

def test_find_by_ref_returns_none_for_unknown_ref(monkeypatch):
    monkeypatch.setattr("models.prescription.load_prescriptions",lambda:[])
    assert models.prescription.find_by_ref("RX-DOES-NOT-EXIST") is None

def test_make_ref():
    prescriptions=[
        models.prescription.Prescription("RX-0001","John Maina",1,"Amoxicillin","2026-09-12","2026-12-31",False),
        models.prescription.Prescription("RX-0002","Jane Doe",2,"Panadol","2026-09-12","2026-12-31",False)
    ]
    assert models.prescription.make_ref(prescriptions)=="RX-0003"

def test_make_ref_empty_list():
    assert models.prescription.make_ref([])=="RX-0001"

def test_issue_prescription_creates_record(monkeypatch):
    doctor=SimpleNamespace(id=1,role="doctor")
    data=[]

    monkeypatch.setattr("models.prescription.load_prescriptions",lambda:data)
    monkeypatch.setattr("models.prescription.save_prescriptions",lambda rows:data.extend(rows))
    monkeypatch.setattr("models.prescription.make_ref",lambda rows:"RX-0001")

    prescription=models.prescription.issue_prescription(
        doctor,
        "John Maina",
        "Amoxicillin",
        "2026-12-31"
    )

    assert prescription.ref=="RX-0001"
    assert prescription.patient_name=="John Maina"
    assert prescription.drug_name=="Amoxicillin"
    assert prescription.doctor_id==1
    assert prescription.used is False

def test_only_doctor_can_issue_prescription():
    customer=SimpleNamespace(id=2,role="customer")

    try:
        models.prescription.issue_prescription(
            customer,
            "John Maina",
            "Amoxicillin",
            "2026-12-31"
        )
        assert False
    except Exception:
        assert True

def test_get_prescription(monkeypatch):
    prescription=models.prescription.Prescription(
        "RX-0006",
        "John Maina",
        1,
        "Amoxicillin",
        "2026-09-12",
        "2026-12-31",
        False
    )

    monkeypatch.setattr("models.prescription.load_prescriptions",lambda:[prescription])

    found=models.prescription.get_prescription("RX-0006")
    assert found.ref=="RX-0006"

def test_get_prescription_unknown_ref(monkeypatch):
    monkeypatch.setattr("models.prescription.load_prescriptions",lambda:[])
    assert models.prescription.get_prescription("RX-DOES-NOT-EXIST") is None