import pytest

from models import drug
from models.drug import add_drug, list_drugs, get_drug


class TestDrug:

    def setup_method(self):
        drug._store.drugs.clear()

    def test_add_drug_creates_a_drug_with_correct_details(self):
        drug_item = add_drug(
            name="Panadol",
            price=50,
            stock=20,
            requires_prescription=False,
            category="analgesic",
        )

        assert drug_item.name == "Panadol"
        assert drug_item.price == 50
        assert drug_item.stock == 20
        assert drug_item.requires_prescription is False

    def test_add_drug_rejects_a_zero_or_negative_price(self):
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

    def test_add_drug_rejects_a_zero_or_negative_stock(self):
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

    def test_list_drugs_returns_every_drug_that_was_added(self):
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

    def test_get_drug_returns_the_matching_drug(self):
        added = add_drug(
            name="Panadol",
            price=50,
            stock=20,
            requires_prescription=False
        )

        found = get_drug(added.id)

        assert found.name == "Panadol"

    def test_get_drug_raises_a_clean_error_for_an_unknown_id(self):
        with pytest.raises(ValueError):
            get_drug("does-not-exist")