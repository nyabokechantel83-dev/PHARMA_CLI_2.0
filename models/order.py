from datetime import date
class Order:
    def __init__(self, id, customer_id,drug_id, category, prescription_ref, status):
        self.id = id
        self.customer_id = customer_id
        self.drug_id = drug_id
        self.category = category
        self.prescription_ref = prescription_ref
        self.status = status
        self.verification_status = None
        self.created_at = date.today()

    def __repr__(self):
        return f"Order(id={self.id!r}, status={self.status!r}, drug_id={self.drug_id!r}" 

class OrderServices:
    def __init__(self, drug_services, prescription_services):
        self._drug_services = drug_services
        self._prescription_services = prescription_services
        self._orders = []
        self._next_id = 1

    def place_order(self, customer, drug_id, prescription_ref=None):
        drug = self._drug_service.get_drug(drug_id)
        if drug.requires_prescription:
            if not prescription_ref:
                raise ValueError(f"'{drug.name}' requires a prescription.")
            status = "pending"

        else :
            prescription_ref = None
            status = "confirmed"

        order = order(
            id=f"order-{self._next_id}",
            customer_id=customer.id,
            drug_id=drug.id,
            category=getattr(drug, "category", None),
            prescription_ref=prescription_ref,
            status=status,          
         )
        self._next_id += 1
        self._orders.append(order)
        return order

    def get_order(self, order_id):
        for order in self._orders:
            if order.id == order_id:
                return order
        raise ValueError(f"No order found with id '{order_id}'.")

    def list_orders_for_customer(self, customer_id):
        return [o for o in self._orders if o.customer_id == customer_id]
 
    def list_pending_claims(self):
        return [o for o in self._orders if o.status == "pending"]
 
    def set_verification_status(self, order_id, status):
        order = self.get_order(order_id)
        order.verification_status = status
        return order

    def decide(self, order_id, approve):
        order = self.get_order(order_id)
        if order.status != "pending":
            raise ValueError(f"Order '{order_id}' is not pending(status: {order.status}).")

        if approve:
            order.status = "approved"
            drug = self._drug_services.get_drug(order.drug_id)
            drug.stock -= 1

            if order.prescription_ref:
                prescription = self._prescription_services.get(order.prescription_ref)
                if prescription is not None:
                    prescription.used = True
            else:
                order.status = "rejected"
            return order
