from models.prescription import Prescription,load_prescriptions,save_prescriptions,find_by_ref,make_ref

def test_prescription_to_dict():
    prescription=Prescription(
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
    prescription=Prescription.from_dict(data)
    assert prescription.ref=="RX-0002"
    assert prescription.patient_name=="Jane Doe"
    assert prescription.doctor_id==2
    assert prescription.drug_name=="Panadol"
    assert prescription.used is False

def test_save_and_load_prescriptions(monkeypatch):
    data=[]
    monkeypatch.setattr(
        "models.prescription.storage.write_json",
        lambda file_name,rows:data.extend(rows)
    )
    monkeypatch.setattr(
        "models.prescription.storage.read_json",
        lambda file_name:data
    )

    prescription=Prescription(
        ref="RX-0003",
        patient_name="John Maina",
        doctor_id=1,
        drug_name="Amoxicillin",
        date_issued="2026-09-12",
        expires_at="2026-12-31",
        used=False
    )

    save_prescriptions([prescription])
    loaded=load_prescriptions()

    assert len(loaded)==1
    assert loaded[0].ref=="RX-0003"
    assert loaded[0].patient_name=="John Maina"
    assert loaded[0].drug_name=="Amoxicillin"

def test_find_by_ref(monkeypatch):
    prescription=Prescription(
        ref="RX-0004",
        patient_name="John Maina",
        doctor_id=1,
        drug_name="Amoxicillin",
        date_issued="2026-09-12",
        expires_at="2026-12-31",
        used=False
    )

    monkeypatch.setattr(
        "models.prescription.load_prescriptions",
        lambda:[prescription]
    )

    found=find_by_ref("RX-0004")
    assert found is prescription

def test_find_by_ref_is_case_insensitive(monkeypatch):
    prescription=Prescription(
        ref="RX-0005",
        patient_name="John Maina",
        doctor_id=1,
        drug_name="Amoxicillin",
        date_issued="2026-09-12",
        expires_at="2026-12-31",
        used=False
    )

    monkeypatch.setattr(
        "models.prescription.load_prescriptions",
        lambda:[prescription]
    )

    found=find_by_ref("rx-0005")
    assert found is prescription

def test_find_by_ref_returns_none_for_unknown_ref(monkeypatch):
    monkeypatch.setattr(
        "models.prescription.load_prescriptions",
        lambda:[]
    )

    assert find_by_ref("RX-DOES-NOT-EXIST") is None

def test_make_ref():
    prescriptions=[
        Prescription(
            ref="RX-0001",
            patient_name="John Maina",
            doctor_id=1,
            drug_name="Amoxicillin",
            date_issued="2026-09-12",
            expires_at="2026-12-31",
            used=False
        ),
        Prescription(
            ref="RX-0002",
            patient_name="Jane Doe",
            doctor_id=2,
            drug_name="Panadol",
            date_issued="2026-09-12",
            expires_at="2026-12-31",
            used=False
        )
    ]

    assert make_ref(prescriptions)=="RX-0003"

def test_make_ref_empty_list():
    assert make_ref([])=="RX-0001"