from types import SimpleNamespace

import pytest

from cli import pharmacist
from utils import verify


def pharmacist_user():
    return SimpleNamespace(id=1, name="Dr. Amina", role="pharmacist")


def customer_user():
    return SimpleNamespace(id=2, name="Kevin", role="customer")


def make_drug(id=1, name="Paracetamol", price=10.0, stock=5, category="painkiller", requires_rx=False):
    return SimpleNamespace(
        id=id, name=name, price=price, stock=stock, category=category, requires_rx=requires_rx
    )


def make_order(
    id=1,
    customer_id=2,
    drug_id=1,
    status="pending",
    created_at="2026-01-01",
    prescription_ref="RX-1",
    verification_status="verified",
):
    return SimpleNamespace(
        id=id,
        customer_id=customer_id,
        drug_id=drug_id,
        status=status,
        created_at=created_at,
        prescription_ref=prescription_ref,
        verification_status=verification_status,
    )


@pytest.fixture(autouse=True)
def patch_status_constants(monkeypatch):
    monkeypatch.setattr(pharmacist.order_model, "STATUS_PENDING", "pending", raising=False)
    monkeypatch.setattr(pharmacist.order_model, "STATUS_APPROVED", "approved", raising=False)
    monkeypatch.setattr(pharmacist.order_model, "STATUS_REJECTED", "rejected", raising=False)


class TestAddDrug:
    def test_adds_drug_and_saves(self, monkeypatch, capsys):
        saved = {}
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        monkeypatch.setattr(pharmacist.drug_model, "save_drugs", lambda drugs: saved.setdefault("drugs", drugs))
        monkeypatch.setattr(pharmacist.storage, "next_id", lambda drugs: 1)
        monkeypatch.setattr(pharmacist, "Drug", lambda **kwargs: SimpleNamespace(**kwargs))

        args = SimpleNamespace(name="Ibuprofen", price=5.5, stock=20, category="painkiller", requires_rx=False)
        pharmacist.add_drug(args, pharmacist_user())

        assert len(saved["drugs"]) == 1
        assert saved["drugs"][0].name == "Ibuprofen"
        out = capsys.readouterr().out
        assert "Ibuprofen" in out
        assert "over the counter" in out

    def test_rejects_negative_price(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        args = SimpleNamespace(name="X", price=-1, stock=5, category="general", requires_rx=False)
        with pytest.raises(ValueError):
            pharmacist.add_drug(args, pharmacist_user())

    def test_rejects_negative_stock(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        args = SimpleNamespace(name="X", price=1, stock=-5, category="general", requires_rx=False)
        with pytest.raises(ValueError):
            pharmacist.add_drug(args, pharmacist_user())

    def test_requires_pharmacist_role(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        args = SimpleNamespace(name="X", price=1, stock=5, category="general", requires_rx=False)
        with pytest.raises(PermissionError):
            pharmacist.add_drug(args, customer_user())


class TestRestock:
    def test_adds_units_to_existing_drug(self, monkeypatch, capsys):
        drug = make_drug(id=1, stock=5)
        saved = {}
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [drug])
        monkeypatch.setattr(pharmacist.drug_model, "save_drugs", lambda drugs: saved.setdefault("drugs", drugs))

        args = SimpleNamespace(drug_id=1, amount=10)
        pharmacist.restock(args, pharmacist_user())

        assert drug.stock == 15
        out = capsys.readouterr().out
        assert "New stock: 15" in out

    def test_rejects_zero_or_negative_amount(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [make_drug()])
        args = SimpleNamespace(drug_id=1, amount=0)
        with pytest.raises(ValueError):
            pharmacist.restock(args, pharmacist_user())

    def test_unknown_drug_id_raises(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [make_drug(id=1)])
        args = SimpleNamespace(drug_id=999, amount=5)
        with pytest.raises(ValueError):
            pharmacist.restock(args, pharmacist_user())


class TestListDrugs:
    def test_prints_message_when_empty(self, monkeypatch, capsys):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        pharmacist.list_drugs(SimpleNamespace(), pharmacist_user())
        out = capsys.readouterr().out
        assert "inventory is empty" in out

    def test_prints_each_drug(self, monkeypatch, capsys):
        drugs = [make_drug(id=1, name="Amoxicillin", requires_rx=True), make_drug(id=2, name="Vitamin C")]
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: drugs)
        pharmacist.list_drugs(SimpleNamespace(), pharmacist_user())
        out = capsys.readouterr().out
        assert "Amoxicillin" in out
        assert "Rx" in out
        assert "Vitamin C" in out
        assert "OTC" in out


class TestDecide:
    def test_approve_dispenses_and_updates_stock(self, monkeypatch, capsys):
        order = make_order(id=1, drug_id=1, verification_status="verified")
        drug = make_drug(id=1, stock=3)
        prescriptions = [SimpleNamespace(ref="RX-1", used=False)]

        monkeypatch.setattr(pharmacist.order_model, "load_orders", lambda: [order])
        monkeypatch.setattr(pharmacist.order_model, "save_orders", lambda orders: None)
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [drug])
        monkeypatch.setattr(pharmacist.drug_model, "save_drugs", lambda drugs: None)
        monkeypatch.setattr(pharmacist.prescription_model, "load_prescriptions", lambda: prescriptions)
        monkeypatch.setattr(pharmacist.prescription_model, "save_prescriptions", lambda p: None)
        monkeypatch.setattr(pharmacist.verify, "VERIFIED", "verified", raising=False)

        args = SimpleNamespace(order_id=1, approve=True, reject=False)
        pharmacist.decide(args, pharmacist_user())

        assert order.status == "approved"
        assert drug.stock == 2
        assert prescriptions[0].used is True
        out = capsys.readouterr().out
        assert "approved" in out

    def test_reject_leaves_stock_untouched(self, monkeypatch, capsys):
        order = make_order(id=1, drug_id=1)
        drug = make_drug(id=1, stock=3)

        monkeypatch.setattr(pharmacist.order_model, "load_orders", lambda: [order])
        monkeypatch.setattr(pharmacist.order_model, "save_orders", lambda orders: None)
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [drug])

        args = SimpleNamespace(order_id=1, approve=False, reject=True)
        pharmacist.decide(args, pharmacist_user())

        assert order.status == "rejected"
        assert drug.stock == 3

    def test_unknown_order_id_raises(self, monkeypatch):
        monkeypatch.setattr(pharmacist.order_model, "load_orders", lambda: [make_order(id=1)])
        args = SimpleNamespace(order_id=999, approve=True, reject=False)
        with pytest.raises(ValueError):
            pharmacist.decide(args, pharmacist_user())

    def test_already_decided_order_raises(self, monkeypatch):
        order = make_order(id=1, status="approved")
        monkeypatch.setattr(pharmacist.order_model, "load_orders", lambda: [order])
        args = SimpleNamespace(order_id=1, approve=True, reject=False)
        with pytest.raises(ValueError):
            pharmacist.decide(args, pharmacist_user())

    def test_out_of_stock_raises(self, monkeypatch):
        order = make_order(id=1, drug_id=1, verification_status="verified")
        drug = make_drug(id=1, stock=0)

        monkeypatch.setattr(pharmacist.order_model, "load_orders", lambda: [order])
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [drug])
        monkeypatch.setattr(pharmacist.verify, "VERIFIED", "verified", raising=False)

        args = SimpleNamespace(order_id=1, approve=True, reject=False)
        with pytest.raises(ValueError):
            pharmacist.decide(args, pharmacist_user())

    def test_unverified_claim_can_still_be_approved_with_warning(self, monkeypatch, capsys):
        order = make_order(id=1, drug_id=1, verification_status="expired")
        drug = make_drug(id=1, stock=3)
        prescriptions = []

        monkeypatch.setattr(pharmacist.order_model, "load_orders", lambda: [order])
        monkeypatch.setattr(pharmacist.order_model, "save_orders", lambda orders: None)
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [drug])
        monkeypatch.setattr(pharmacist.drug_model, "save_drugs", lambda drugs: None)
        monkeypatch.setattr(pharmacist.prescription_model, "load_prescriptions", lambda: prescriptions)
        monkeypatch.setattr(pharmacist.prescription_model, "save_prescriptions", lambda p: None)
        monkeypatch.setattr(pharmacist.verify, "VERIFIED", "verified", raising=False)
        monkeypatch.setattr(pharmacist.verify, "describe", lambda status: f"status was {status}")

        args = SimpleNamespace(order_id=1, approve=True, reject=False)
        pharmacist.decide(args, pharmacist_user())

        out = capsys.readouterr().out
        assert "WARNING" in out
        assert order.status == "approved"


class TestMarkPrescriptionUsed:
    def test_marks_matching_prescription_used(self, monkeypatch):
        prescriptions = [SimpleNamespace(ref="RX-1", used=False), SimpleNamespace(ref="RX-2", used=False)]
        monkeypatch.setattr(pharmacist.prescription_model, "load_prescriptions", lambda: prescriptions)
        saved = {}
        monkeypatch.setattr(
            pharmacist.prescription_model, "save_prescriptions", lambda p: saved.setdefault("p", p)
        )

        pharmacist.mark_prescription_used("rx-1")

        assert prescriptions[0].used is True
        assert prescriptions[1].used is False
        assert saved["p"] is prescriptions

    def test_none_ref_does_nothing(self, monkeypatch):
        called = {"load": False}
        monkeypatch.setattr(
            pharmacist.prescription_model, "load_prescriptions", lambda: called.__setitem__("load", True)
        )
        pharmacist.mark_prescription_used(None)
        assert called["load"] is False