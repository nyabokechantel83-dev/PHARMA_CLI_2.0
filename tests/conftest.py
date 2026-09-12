import pytest

from models.user import UserService
from models.drug import DrugService
from models.prescription import PrescriptionService
from models.order import OrderService
from utils.verify import VerificationService


@pytest.fixture
def user_service():
    return UserService()


@pytest.fixture
def drug_service():
    return DrugService()


@pytest.fixture
def prescription_service():
    return PrescriptionService()


@pytest.fixture
def order_service(drug_service, prescription_service):
    return OrderService(drug_service=drug_service, prescription_service=prescription_service)


@pytest.fixture
def verification_service(prescription_service, order_service):
    return VerificationService(prescription_service=prescription_service, order_service=order_service)


@pytest.fixture
def pharmacist(user_service):
    return user_service.register(
        name="Amina Mohammed",
        email="amina@pharmacy.co.ke",
        password="Str0ngPass!",
        role="pharmacist",
    )


@pytest.fixture
def customer(user_service):
    return user_service.register(
        name="Josephine Njuguna",
        email="josephine@example.com",
        password="Str0ngPass!",
        role="customer",
    )


@pytest.fixture
def doctor(user_service):
    return user_service.register(
        name="Dr. Kariuki",
        email="kariuki@hospital.co.ke",
        password="Str0ngPass!",
        role="doctor",
    )


class FakeAuthService:
    def __init__(self, current_user):
        self.current_user = current_user

    def get_current_user(self):
        return self.current_user


class Services:
    def __init__(self, drug, order, prescription, verify, auth):
        self.drug = drug
        self.order = order
        self.prescription = prescription
        self.verify = verify
        self.auth = auth


@pytest.fixture
def services(drug_service, order_service, prescription_service, verification_service, customer):
    return Services(
        drug=drug_service,
        order=order_service,
        prescription=prescription_service,
        verify=verification_service,
        auth=FakeAuthService(current_user=customer),
    )