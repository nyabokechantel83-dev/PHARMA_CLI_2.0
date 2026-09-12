from types import SimpleNamespace

import pytest

from cli import pharmacist
from utils import auth, verify


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
        pharmacist.add_drug.__wrapped__(args, pharmacist_user())

        assert len(saved["drugs"]) == 1
        assert saved["drugs"][0].name == "Ibuprofen"
        out = capsys.readouterr().out
        assert "Ibuprofen" in out
        assert "over the counter" in out

    def test_rejects_negative_price(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        args = SimpleNamespace(name="X", price=-1, stock=5, category="general", requires_rx=False)
        with pytest.raises(ValueError):
            pharmacist.add_drug.__wrapped__(args, pharmacist_user())

    def test_rejects_negative_stock(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        args = SimpleNamespace(name="X", price=1, stock=-5, category="general", requires_rx=False)
        with pytest.raises(ValueError):
            pharmacist.add_drug.__wrapped__(args, pharmacist_user())

    def test_requires_pharmacist_role(self, monkeypatch):
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [])
        # Go through the decorator here on purpose: it is the role check
        # itself we want to prove, and it reads the logged-in user.
        monkeypatch.setattr(auth, "current_user", customer_user)
        args = SimpleNamespace(name="X", price=1, stock=5, category="general", requires_rx=False)
        with pytest.raises(PermissionError):
            pharmacist.add_drug(args)


class TestRestock:
    def test_adds_units_to_existing_drug(self, monkeypatch, capsys):
        drug = make_drug(id=1, stock=5)
        saved = {}
        monkeypatch.setattr(pharmacist.drug_model, "load_drugs", lambda: [drug])
        monkeypatch.setattr(pharmacist.drug_model, "save_drugs", lambda drugs: saved.setdefault("drugs", drugs))

        args = SimpleNamespace(drug_id=1, amount=10)
        pharmacist.restock.__wrapped__(args, pharmacist_user())

        assert drug.stock == 15
        out = capsys.readouterr().out
        assert "New stock: 15" in out

    def test_rejects_zero_or_negative_amount(self, monkeypatch):