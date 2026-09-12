from dataclasses import dataclass,asdict
from datetime import date
from utils import storage

FILE_NAME="prescriptions.json"

@dataclass
class Prescription:
    ref:str
    patient_name:str
    doctor_id:int
    drug_name:str
    date_issued:str
    expires_at:str
    used:bool

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(row):
        return Prescription(**row)

def load_prescriptions():
    rows=storage.read_json(FILE_NAME)
    return [Prescription.from_dict(row) for row in rows]

def save_prescriptions(prescriptions):
    rows=[prescription.to_dict() for prescription in prescriptions]
    storage.write_json(FILE_NAME,rows)

def find_by_ref(ref):
    for prescription in load_prescriptions():
        if prescription.ref.upper()==ref.upper():
            return prescription
    return None

def make_ref(prescriptions):
    number=len(prescriptions)+1
    return f"RX-{number:04d}"

def issue_prescription(doctor,patient_name,drug_name,expires_at):
    if getattr(doctor,"role",None)!="doctor":
        raise Exception("Only a doctor can issue a prescription")
    prescriptions=load_prescriptions()
    prescription=Prescription(
        ref=make_ref(prescriptions),
        patient_name=patient_name,
        doctor_id=doctor.id,
        drug_name=drug_name,
        date_issued=date.today().isoformat(),
        expires_at=expires_at,
        used=False
    )
    prescriptions.append(prescription)
    save_prescriptions(prescriptions)
    return prescription

def get_prescription(ref):
    return find_by_ref(ref)