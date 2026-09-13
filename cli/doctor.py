from datetime import date,timedelta
from models import prescription as prescription_model
from models.prescription import Prescription
from utils.auth import requires_role

DEFAULT_DAYS_VALID=30

def add_commands(subparsers):
    issue_parser=subparsers.add_parser("issue-prescription",help="[doctor] Write a prescription for a patient")
    issue_parser.add_argument("--patient-name",required=True)
    issue_parser.add_argument("--drug-name",required=True)
    issue_parser.add_argument("--days-valid",type=int,default=DEFAULT_DAYS_VALID)
    issue_parser.set_defaults(func=issue_prescription)

    list_parser=subparsers.add_parser("list-prescriptions",help="[doctor] Show prescriptions")
    list_parser.set_defaults(func=list_prescriptions)

@requires_role("doctor")
def issue_prescription(args,user):
    if args.days_valid<1:
        raise ValueError("--days-valid must be at least 1")

    prescriptions=prescription_model.load_prescriptions()
    today=date.today()
    expires=today+timedelta(days=args.days_valid)

    prescription=Prescription(
        ref=prescription_model.make_ref(prescriptions),
        patient_name=args.patient_name,
        doctor_id=user.id,
        drug_name=args.drug_name,
        date_issued=today.isoformat(),
        expires_at=expires.isoformat(),
        used=False
    )

    prescriptions.append(prescription)
    prescription_model.save_prescriptions(prescriptions)

    print(f"Prescription created: {prescription.ref}")
    print(f"Patient: {prescription.patient_name}")
    print(f"Drug: {prescription.drug_name}")
    print(f"Expires: {prescription.expires_at}")
    print(f"Give the reference {prescription.ref} to the patient.")

@requires_role("doctor")
def list_prescriptions(args,user):
    del args
    prescriptions=prescription_model.load_prescriptions()
    mine=[p for p in prescriptions if p.doctor_id==user.id]

    if not mine:
        print("No prescriptions found")
        return

    print(f"{'REF':<10}{'PATIENT':<20}{'DRUG':<20}{'EXPIRES':<12}USED")
    print("-"*70)

    for prescription in mine:
        used="yes" if prescription.used else "no"
        print(f"{prescription.ref:<10}{prescription.patient_name:<20}{prescription.drug_name:<20}{prescription.expires_at:<12}{used}")