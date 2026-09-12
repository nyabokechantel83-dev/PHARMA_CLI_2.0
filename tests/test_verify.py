from datetime import date

from models import order as order_model
from models import prescription as prescription_model
from models.drug import Drug
from models.order import Order
from models.prescription import Prescription
from utils import verify


TODAY = date(2026, 6, 1)


def make_drug(name="Amoxicillin", requires_rx=True, drug_id=1):
    return Drug(
        id=drug_id,
        name=name,
        price=350.0,
        stock=10,
        category="antibiotic",
        requires_rx=requires_rx,
    )


def save_prescription(patient_name="Ann Customer", 
                      drug_name="Amoxicillin",
                      expires_at="2026-07-01", 
                      used=False):
    prescription_model.save_prescriptions([
        Prescription(
            ref="RX-0001",
            patient_name=patient_name,
            doctor_id=2,
            drug_name=drug_name,
            date_issued="2026-05-01",
            expires_at=expires_at,
            used=used,
        )
    ])


def test_a_good_prescription_is_verified(customer_user):
    save_prescription()

    result = verify.check_prescription("RX-0001", make_drug(), customer_user, today=TODAY)

    assert result == verify.VERIFIED


def test_an_invented_reference_is_not_found(customer_user):
    save_prescription()

    result = verify.check_prescription("RX-9999", make_drug(), customer_user, today=TODAY)

    assert result == verify.NOT_FOUND


def test_a_prescription_for_another_drug_is_a_mismatch(customer_user):
    save_prescription(drug_name="Amoxicillin")

    result = verify.check_prescription(
        "RX-0001", make_drug(name="Diazepam"), customer_user, today=TODAY
    )

    assert result == verify.DRUG_MISMATCH


def test_somebody_elses_prescription_is_a_mismatch(customer_user):
    save_prescription(patient_name="Brian Other")

    result = verify.check_prescription("RX-0001", make_drug(), customer_user, today=TODAY)

    assert result == verify.NAME_MISMATCH


def test_an_old_prescription_is_expired(customer_user):
    save_prescription(expires_at="2026-05-20")

    result = verify.check_prescription("RX-0001", make_drug(), customer_user, today=TODAY)

    assert result == verify.EXPIRED


def test_a_prescription_that_expires_today_still_works(customer_user):
    save_prescription(expires_at=TODAY.isoformat())

    result = verify.check_prescription("RX-0001", make_drug(), customer_user, today=TODAY)

    assert result == verify.VERIFIED


def test_a_used_prescription_cannot_be_used_again(customer_user):
    save_prescription(used=True)

    result = verify.check_prescription("RX-0001", make_drug(), customer_user, today=TODAY)

    assert result == verify.ALREADY_USED


def test_the_reference_is_not_case_sensitive(customer_user):
    save_prescription()

    result = verify.check_prescription("rx-0001", make_drug(), customer_user, today=TODAY)

    assert result == verify.VERIFIED


def save_past_orders(customer_id, how_many, order_date, drug_id=1):
    orders = []

    for number in range(how_many):
        orders.append(
            Order(
                id=number + 1,
                customer_id=customer_id,
                drug_id=drug_id,
                prescription_ref=None,
                status=order_model.STATUS_COMPLETED,
                verification_status=verify.NOT_REQUIRED,
                created_at=order_date,
            )
        )

    order_model.save_orders(orders)


def test_a_first_purchase_raises_no_advisory(customer_user):
    otc_drug = make_drug(name="Panadol", requires_rx=False)

    assert verify.otc_advisory(customer_user, otc_drug, today=TODAY) is None


def test_a_third_purchase_in_the_window_raises_an_advisory(customer_user):
    otc_drug = make_drug(name="Panadol", requires_rx=False)
    save_past_orders(customer_user.id, 2, "2026-05-25")

    message = verify.otc_advisory(customer_user, otc_drug, today=TODAY)

    assert message is not None
    assert "Panadol" in message
    assert "3 times" in message


def test_old_purchases_fall_out_of_the_window(customer_user):
    otc_drug = make_drug(name="Panadol", requires_rx=False)
    save_past_orders(customer_user.id, 5, "2026-01-10")

    assert verify.otc_advisory(customer_user, otc_drug, today=TODAY) is None


def test_prescription_drugs_never_raise_an_advisory(customer_user):
    rx_drug = make_drug(requires_rx=True)
    save_past_orders(customer_user.id, 5, "2026-05-25")

    assert verify.otc_advisory(customer_user, rx_drug, today=TODAY) is None