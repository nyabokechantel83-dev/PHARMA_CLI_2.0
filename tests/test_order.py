from models.order import (
    Order,
    load_orders,
    save_orders,
    find_by_id,
    orders_for_customer
)


def test_order_to_dict():
    order = Order(
        id=1,
        customer_id=10,
        drug_id=5,
        prescription_ref="RX-1001",
        status="pending",
        verification_status="verified",
        created_at="2026-09-12"
    )

    result = order.to_dict()

    assert result["id"] == 1
    assert result["customer_id"] == 10
    assert result["drug_id"] == 5
    assert result["prescription_ref"] == "RX-1001"
    assert result["status"] == "pending"
    assert result["verification_status"] == "verified"
    assert result["created_at"] == "2026-09-12"


def test_order_from_dict():
    data = {
        "id": 1,
        "customer_id": 10,
        "drug_id": 5,
        "prescription_ref": "RX-1001",
        "status": "pending",
        "verification_status": "verified",
        "created_at": "2026-09-12"
    }

    order = Order.from_dict(data)

    assert order.id == 1
    assert order.customer_id == 10
    assert order.drug_id == 5
    assert order.prescription_ref == "RX-1001"


def test_save_and_load_orders(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    orders = [
        Order(
            id=1,
            customer_id=10,
            drug_id=5,
            prescription_ref="RX-1001",
            status="pending",
            verification_status="verified",
            created_at="2026-09-12"
        )
    ]

    save_orders(orders)
    loaded_orders = load_orders()

    assert len(loaded_orders) == 1
    assert loaded_orders[0].id == 1
    assert loaded_orders[0].customer_id == 10
    assert loaded_orders[0].drug_id == 5


def test_find_by_id(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    orders = [
        Order(1, 10, 5, "RX-1001", "pending", "verified", "2026-09-12"),
        Order(2, 20, 6, None, "pending", "not_required", "2026-09-12")
    ]

    save_orders(orders)

    order = find_by_id(2)

    assert order is not None
    assert order.id == 2
    assert order.customer_id == 20


def test_find_by_id_returns_none_when_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    save_orders([])

    result = find_by_id(999)

    assert result is None


def test_orders_for_customer(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    orders = [
        Order(1, 10, 5, "RX-1001", "pending", "verified", "2026-09-12"),
        Order(2, 20, 6, None, "approved", "not_required", "2026-09-12"),
        Order(3, 10, 7, None, "completed", "not_required", "2026-09-12")
    ]

    save_orders(orders)

    customer_orders = orders_for_customer(10)

    assert len(customer_orders) == 2
    assert customer_orders[0].id == 1
    assert customer_orders[1].id == 3