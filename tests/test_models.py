
from models.drug import Drug
from models.order import Order
from models.prescription import Prescription, make_ref
from models.user import User


def test_drug_survives_a_trip_through_a_dictionary():
    original = Drug(
        id=1,
        name="Amoxicillin",
        price=350.0,
        stock=20,
        category="antibiotic",
        requires_rx=True,
    )

    copy = Drug.from_dict(original.to_dict())

    assert copy == original


def test_user_survives_a_trip_through_a_dictionary():
    original = User(
        id=1,
        name="Ann",
        email="ann@mail.com",
        role="customer",
        password_hash="abc",
        salt="def",
    )

    assert User.from_dict(original.to_dict()) == original


def test_prescription_survives_a_trip_through_a_dictionary():
    original = Prescription(
        ref="RX-0001",
        patient_name="Ann",
        doctor_id=2,
        drug_name="Amoxicillin",
        date_issued="2026-01-01",
        expires_at="2026-02-01",
        used=False,
    )

    assert Prescription.from_dict(original.to_dict()) == original


def test_order_survives_a_trip_through_a_dictionary():
    original = Order(
        id=1,
        customer_id=3,
        drug_id=1,
        prescription_ref="RX-0001",
        status="pending",
        verification_status="verified",
        created_at="2026-01-01",
    )

    assert Order.from_dict(original.to_dict()) == original


def test_prescription_references_are_numbered_and_padded():
    assert make_ref([]) == "RX-0001"
    assert make_ref([1, 2, 3]) == "RX-0004"
