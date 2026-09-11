from datetime import date, timedelta
class VerificationServices:
    def __init__(self, prescription_services, order_service):
        self._prescription_services = prescription_services
        self._order_services = order_service

    def verify_prescription(self, ref, drug_name):
        prescription = self._prescription_services.get(ref)
        if prescription is None:
            return "not_found"

        if prescription.used:
            return "already_used"

        if self._is_expired(prescription.expires_at):
            return "expired"

        return "verified"

    @staticmethod
    def _is_expired(expires_at):
        expiry_date = date.fromisoformat(expires_at)
        return expiry_date < date.today()

    def otc_advisory(self, customer_id, category, threshold=3, window_days=7):
        cutoff = date.today() - timedelta(days=window_days)
        customer_orders = self._order_services.list_orders_for_customer(customer_id)
        recent_matching_orders = [
            o for o in customer_orders
            if o.category == category and o.created_at >= cutoff
        ]

        if len(recent_matching_orders) >= threshold:
            return (
                f"Advisory: {len(recent_matching_orders)} '{category}' purchases "
                f"in the las {window_days} days. Consider recommending a "
                f"pharmacist consultation."
            )

        return None

