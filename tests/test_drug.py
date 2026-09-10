"""
Tests for models/drug.py — the pharmacist's inventory.

Plain-English summary:
- Adding a drug with valid details should work.
- Adding a drug with price <= 0 or stock <= 0 should be rejected.
- Listing drugs should return everything that's been added.
- Showing one drug by id should work, and a bad id should give a
  clean error instead of crashing.
"""

import pytest

from models import drug
from models.drug import add_drug, list_drugs, get_drug


@pytest.fixture(autouse=True)
def clear_store():
    drug._store.drugs.clear()


def test_add_drug_creates_a_drug_with_correct_details():
    drug = add_drug(
        name="Panadol",
        price=50,
        stock=20,
        requires_prescription=False,
        category="analgesic",
    )

    assert drug.name == "Panadol"
    assert drug.price == 50
    assert drug.stock == 20
    assert drug.requires_prescription is False


def test_add_drug_rejects_a_zero_or_negative_price():
    with pytest.raises(ValueError):
        add_drug(
            name="Panadol",
            price=0,
            stock=10,
            requires_prescription=False
        )

    with pytest.raises(ValueError):
        add_drug(
            name="Panadol",
            price=-5,
            stock=10,
            requires_prescription=False
        )


def test_add_drug_rejects_a_zero_or_negative_stock():
    with pytest.raises(ValueError):
        add_drug(
            name="Panadol",
            price=50,
            stock=0,
            requires_prescription=False
        )

    with pytest.raises(ValueError):
        add_drug(
            name="Panadol",
            price=50,
            stock=-3,
            requires_prescription=False
        )


def test_list_drugs_returns_every_drug_that_was_added():
    add_drug(
        name="Panadol",
        price=50,
        stock=20,
        requires_prescription=False
    )

    add_drug(
        name="Amoxicillin",
        price=150,
        stock=10,
        requires_prescription=True
    )

    drugs = list_drugs()

    assert len(drugs) == 2

    names = [drug.name for drug in drugs]

    assert "Panadol" in names
    assert "Amoxicillin" in names


def test_get_drug_returns_the_matching_drug():
    added = add_drug(
        name="Panadol",
        price=50,
        stock=20,
        requires_prescription=False
    )

    found = get_drug(added.id)

    assert found.name == "Panadol"


def test_get_drug_raises_a_clean_error_for_an_unknown_id():
    with pytest.raises(ValueError):
        get_drug("does-not-exist")