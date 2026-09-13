from dataclasses import dataclass, asdict

from utils import storage

FILE_NAME = "orders.json"


STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_COMPLETED = "completed"


@dataclass
class Order:
    id: int
    customer_id: int
    drug_id: int
    prescription_ref: str | None
    status: str
    verification_status: str
    created_at: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(row):
        return Order(**row)


def load_orders():
    rows = storage.read_json(FILE_NAME)
    return [Order.from_dict(row) for row in rows]


def save_orders(orders):
    rows = [order.to_dict() for order in orders]
    storage.write_json(FILE_NAME, rows)


def find_by_id(order_id):
    for order in load_orders():
        if order.id == order_id:
            return order

    return None


def orders_for_customer(customer_id):
    return [order for order in load_orders() if order.customer_id == customer_id]