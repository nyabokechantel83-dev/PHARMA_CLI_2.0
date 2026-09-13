import pytest

from models import drug as drug_model
from models.drug import Drug


def make_row(id=1, name="Paracetamol", price=10.0, stock=5, category="painkiller", requires_rx=False):
    return {
        "id": id,
        "name": name,
        "price": price,
        "stock": stock,
        "category": category,
        "requires_rx": requires_rx,
    }


class TestDrugDataclass:
    def test_to_dict_returns_plain_dict(self):
        drug = Drug(id=1, name="Ibuprofen", price=5.5, stock=20, category="painkiller", requires_rx=False)
        assert drug.to_dict() == {
            "id": 1,
            "name": "Ibuprofen",
            "price": 5.5,
            "stock": 20,
            "category": "painkiller",
            "requires_rx": False,
        }

    def test_from_dict_builds_matching_drug(self):
        row = make_row(id=2, name="Amoxicillin", requires_rx=True)
        drug = Drug.from_dict(row)
        assert drug.id == 2
        assert drug.name == "Amoxicillin"
        assert drug.requires_rx is True

    def test_round_trip_through_dict(self):
        original = Drug(id=3, name="Vitamin C", price=3.0, stock=100, category="supplement", requires_rx=False)
        rebuilt = Drug.from_dict(original.to_dict())
        assert rebuilt == original


class TestLoadDrugs:
    def test_returns_drug_objects_from_storage(self, monkeypatch):
        rows = [make_row(id=1, name="A"), make_row(id=2, name="B")]
        monkeypatch.setattr(drug_model.storage, "read_json", lambda filename: rows)

        drugs = drug_model.load_drugs()

        assert len(drugs) == 2
        assert all(isinstance(d, Drug) for d in drugs)
        assert drugs[0].name == "A"
        assert drugs[1].name == "B"

    def test_reads_from_correct_file(self, monkeypatch):
        seen = {}

        def fake_read_json(filename):
            seen["filename"] = filename
            return []

        monkeypatch.setattr(drug_model.storage, "read_json", fake_read_json)
        drug_model.load_drugs()
        assert seen["filename"] == drug_model.FILE_NAME

    def test_empty_storage_returns_empty_list(self, monkeypatch):
        monkeypatch.setattr(drug_model.storage, "read_json", lambda filename: [])
        assert drug_model.load_drugs() == []


class TestSaveDrugs:
    def test_writes_drugs_as_dicts(self, monkeypatch):
        saved = {}
        monkeypatch.setattr(
            drug_model.storage,
            "write_json",
            lambda filename, rows: saved.update(filename=filename, rows=rows),
        )

        drugs = [
            Drug(id=1, name="A", price=1.0, stock=1, category="general", requires_rx=False),
            Drug(id=2, name="B", price=2.0, stock=2, category="general", requires_rx=True),
        ]
        drug_model.save_drugs(drugs)

        assert saved["filename"] == drug_model.FILE_NAME
        assert saved["rows"] == [drug.to_dict() for drug in drugs]

    def test_writes_empty_list(self, monkeypatch):
        saved = {}
        monkeypatch.setattr(
            drug_model.storage,
            "write_json",
            lambda filename, rows: saved.update(filename=filename, rows=rows),
        )
        drug_model.save_drugs([])
        assert saved["rows"] == []


class TestFindById:
    def test_returns_matching_drug(self, monkeypatch):
        drugs = [Drug(**make_row(id=1)), Drug(**make_row(id=2, name="Other"))]
        monkeypatch.setattr(drug_model, "load_drugs", lambda: drugs)

        found = drug_model.find_by_id(2)

        assert found is not None
        assert found.name == "Other"

    def test_returns_none_when_not_found(self, monkeypatch):
        drugs = [Drug(**make_row(id=1))]
        monkeypatch.setattr(drug_model, "load_drugs", lambda: drugs)

        assert drug_model.find_by_id(999) is None

    def test_returns_none_when_no_drugs(self, monkeypatch):
        monkeypatch.setattr(drug_model, "load_drugs", lambda: [])
        assert drug_model.find_by_id(1) is None