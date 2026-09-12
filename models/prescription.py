import uuid


_prescriptions = {}


class Prescription:
    def __init__( self, ref, patient_name, drug_name, doctor_id, expires_at):
        self.ref = ref
        self.patient_name = patient_name
        self.drug_name = drug_name
        self.doctor_id = doctor_id
        self.expires_at = expires_at
        self.used = False


def issue_prescription(
    doctor,
    patient_name,
    drug_name,
    expires_at,
):
    if getattr(doctor, "role", None) != "doctor":
        raise Exception("Only a doctor can issue a prescription")

    ref = f"RX-{uuid.uuid4().hex[:8].upper()}"

    prescription = Prescription(
        ref=ref,
        patient_name=patient_name,
        drug_name=drug_name,
        doctor_id=doctor.id,
        expires_at=expires_at,
    )

    _prescriptions[ref] = prescription

    return prescription


def get_prescription(ref):
    return _prescriptions.get(ref)