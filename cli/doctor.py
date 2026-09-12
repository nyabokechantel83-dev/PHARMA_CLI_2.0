from utils.auth import requires_role


def register_subparser(subparser, services):
    prescription_parser = subparser.add_parser(
        "issue-prescription",
        help="Issue a prescription to a patient"
    )

    prescription_parser.add_argument(
        "patient_name",
        help="Name of the patient"
    )

    prescription_parser.add_argument(
        "drug_name",
        help="Name of the prescribed drug"
    )

    prescription_parser.add_argument(
        "--expires-at",
        required=True,
        dest="expires_at",
        help="Prescription expiry date"
    )

    prescription_parser.set_defaults(
        func=lambda args: _issue_prescription(args, services)
    )


@requires_role("doctor")
def _issue_prescription_for_current_doctor(
    current_doctor,
    args,
    services
):
    prescription = services.prescription.issue_prescription(
        doctor=current_doctor,
        patient_name=args.patient_name,
        drug_name=args.drug_name,
        expires_at=args.expires_at,
    )

    print(f"Prescription issued successfully.")
    print(f"Reference: {prescription.ref}")
    print(f"Patient: {prescription.patient_name}")
    print(f"Drug: {prescription.drug_name}")
    print(f"Expires: {prescription.expires_at}")


def _issue_prescription(args, services):
    current_user = services.auth.get_current_user()

    try:
        _issue_prescription_for_current_doctor(
            current_doctor=current_user,
            args=args,
            services=services
        )
    except ValueError as error:
        print(f"Error: {error}")
    except Exception as error:
        print(f"Error: {error}")