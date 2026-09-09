"""
Tests for models/order.py — a customer placing an order.

summary:
- Ordering a normal (non-prescription) drug confirms right away.
- Ordering a prescription drug needs a prescription ref and starts
  out "pending" instead of "confirmed".
- Ordering a prescription drug WITHOUT a ref should fail clearly.
"""

import pytest

from models.drug import add_drug
from models.order import place_order


def test_ordering_a_non_prescription_drug_confirms_instantly(customer):
    drug = add_drug(name="Panadol", price=50, stock=20, requires_prescription=False)

    order = place_order(customer=customer, drug_id=drug.id)

    assert order.status == "confirmed"


def test_ordering_a_prescription_drug_with_a_ref_is_pending(customer):
    drug = add_drug(name="Amoxicillin", price=150, stock=10, requires_prescription=True)

    order = place_order(customer=customer, drug_id=drug.id, prescription_ref="RX-1001")

    assert order.status == "pending"
    assert order.prescription_ref == "RX-1001"


def test_ordering_a_prescription_drug_without_a_ref_raises_an_error(customer):
    drug = add_drug(name="Amoxicillin", price=150, stock=10, requires_prescription=True)

    with pytest.raises(ValueError):
        place_order(customer=customer, drug_id=drug.id) 

def test_order_is_linked_to_the_customer_who_placed_it(customer):
    drug = add_drug(name="Panadol", price=50, stock=20, requires_prescription=False)

    order = place_order(customer=customer, drug_id=drug.id)

    assert order.customer_id == customer.id