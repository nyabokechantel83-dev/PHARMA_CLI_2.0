import pytest

from utils import auth, storage


@pytest.fixture(autouse=True)
def clean_data(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def pharmacist_user():
    return auth.register("Pam Pharm", "pam@mail.com", "secret123", "pharmacist")


@pytest.fixture
def doctor_user():
    return auth.register("Dr Dan", "dan@mail.com", "secret123", "doctor")


@pytest.fixture
def customer_user():
    return auth.register("Ann Customer", "ann@mail.com", "secret123", "customer")