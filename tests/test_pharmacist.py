import pytest

from cli.pharmacist import Pharmacist


class TestPharmacist:

    def setup_method(self):
        self.pharmacist = Pharmacist(
            "John",
            "data/test_drugs.json"
        )
        self.pharmacist.save_drugs([])

    def test_add_drug(self):
        drug = self.pharmacist.add_drug(
            name="Panadol",
            price=50,
            stock=20,
            requires_prescription=False,
            category="analgesic"
        )

        assert drug["name"] == "Panadol"
        assert drug["price"] == 50
        assert drug["stock"] == 20
        assert drug["requires_prescription"] is False

    def test_add_drug_rejects_invalid_price(self):
        with pytest.raises(ValueError):
            self.pharmacist.add_drug(
                name="Panadol",
                price=0,
                stock=20,
                requires_prescription=False
            )

    def test_add_drug_rejects_invalid_stock(self):
        with pytest.raises(ValueError):
            self.pharmacist.add_drug(
                name="Panadol",
                price=50,
                stock=0,
                requires_prescription=False
            )

    def test_list_drugs(self):
        self.pharmacist.add_drug(
            name="Panadol",
            price=50,
            stock=20,
            requires_prescription=False
        )

        drugs = self.pharmacist.list_drugs()

        assert len(drugs) == 1
        assert drugs[0]["name"] == "Panadol"

    def test_get_drug(self):
        added = self.pharmacist.add_drug(
            name="Panadol",
            price=50,
            stock=20,
            requires_prescription=False
        )

        found = self.pharmacist.get_drug(added["id"])

        assert found["name"] == "Panadol"

    def test_update_stock(self):
        added = self.pharmacist.add_drug(
            name="Panadol",
            price=50,
            stock=20,
            requires_prescription=False
        )

        updated = self.pharmacist.update_stock(added["id"], 30)

        assert updated["stock"] == 30