from dataclasses import dataclass, asdict
from datetime import date

from utils import storage

FILE_NAME = "prescriptions.json"


@dataclass
class Prescription:
    ref: str
    patient_name: str
    doctor_id: int
    drug_name: str
    date_issued: str
    expires_at: str
    used: bool = False

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(row):
        return Prescription(**row)

def load_prescriptions():
    data = storage.read_json(FILE_NAME)
    return [Prescription.from_dict(item) for item in data]

def save_prescriptions(prescriptions):
    data = [p.to_dict() for p in prescriptions]
    storage.write_json(FILE_NAME, data)

def find_by_ref(ref):
    prescriptions = load_prescriptions()
    for p in prescriptions:
        if p.ref.lower() == ref.lower():
            return p
    return None

def make_ref(prescriptions):
    if not prescriptions:
        return "RX-0001"
    
    nums = [int(p.ref.split("-")[1]) for p in prescriptions]
    new_num = max(nums) + 1
    return f"RX-{new_num:04d}"

def issue_prescription(doctor, patient_name, drug_name, expires_at):
    """Write a new prescription and save it. Only a doctor may do this."""
    if getattr(doctor, "role", None) != "doctor":
        raise PermissionError("Only a doctor can issue a prescription.")

    prescriptions = load_prescriptions()

    new_prescription = Prescription(
        ref=make_ref(prescriptions),
        patient_name=patient_name,
        doctor_id=doctor.id,
        drug_name=drug_name,
        date_issued=date.today().isoformat(),
        expires_at=expires_at,
        used=False,
    )

    prescriptions.append(new_prescription)
    save_prescriptions(prescriptions)
    return new_prescription


def get_prescription(ref):
    """Look a prescription up by its reference code, or None if unknown."""
    return find_by_ref(ref)