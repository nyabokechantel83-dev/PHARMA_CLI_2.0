from datetime import date

from models import drug as drug_model
from models import order as order_model
from models.order import Order
from utils import storage, verify
from utils.auth import requires_role


def add_commands(subparsers):
    browse_parser = subparsers.add_parser("browse", help="[customer] Show the drugs on sale")
    browse_parser.set_defaults(func=browse)

    order_parser = subparsers.add_parser("order", help="[customer] Order one unit of a drug")
    order_parser.add_argument("--drug-id", type=int, required=True, help="Id of the drug")
    order_parser.add_argument(
        "--prescription-ref",
        help="Prescription reference, needed only for prescription drugs",
    )
    order_parser.set_defaults(func=place_order)

    my_orders_parser = subparsers.add_parser(
        "my-orders",
        help="[customer] Show the orders you have placed",
    )
    my_orders_parser.set_defaults(func=my_orders)


@requires_role("customer")
def browse(args, user):
    del args, user

    drugs = drug_model.load_drugs()

    if not drugs:
        print("Nothing is on sale yet.")
        return

    print(f"{'ID':<5} {'NAME':<22} {'CATEGORY':<14} {'PRICE':>8} {'STOCK':>6}  NEEDS")
    print("-" * 76)

    for stored_drug in drugs:
        needs_text = "prescription" if stored_drug.requires_rx else "-"
        print(
            f"{stored_drug.id:<5} {stored_drug.name:<22} {(stored_drug.category or '-'):<14} "
            f"{stored_drug.price:>8.2f} {stored_drug.stock:>6}  {needs_text}"
        )


@requires_role("customer")
def place_order(args, user):
    chosen_drug = drug_model.find_by_id(args.drug_id)

    if chosen_drug is None:
        raise ValueError(f"There is no drug with id {args.drug_id}.")

    if chosen_drug.stock < 1:
        raise ValueError(f"{chosen_drug.name} is out of stock.")

    if chosen_drug.requires_rx:
        order_prescription_drug(args, user, chosen_drug)
    else:
        order_otc_drug(user, chosen_drug)


def order_prescription_drug(args, user, chosen_drug):
    if not args.prescription_ref:
        raise ValueError(
            f"{chosen_drug.name} needs a prescription. "
            "Add --prescription-ref RX-0001 to your order."
        )

   
    verification_status = verify.check_prescription(
        args.prescription_ref,
        chosen_drug,
        user,
    )

    orders = order_model.load_orders()

    new_order = Order(
        id=storage.next_id(orders),
        customer_id=user.id,
        drug_id=chosen_drug.id,
        prescription_ref=args.prescription_ref,
        status=order_model.STATUS_PENDING,
        verification_status=verification_status,
        created_at=date.today().isoformat(),
    )

    orders.append(new_order)
    order_model.save_orders(orders)

    print(f"Claim #{new_order.id} created for {chosen_drug.name}.")
    print(f"  Check result: {verify.describe(verification_status)}")
    print()
    print("A pharmacist will review this claim. Nothing has been dispensed yet.")


def order_otc_drug(user, chosen_drug):
    orders = order_model.load_orders()

    advisory_message = verify.otc_advisory(user, chosen_drug)

    new_order = Order(
        id=storage.next_id(orders),
        customer_id=user.id,
        drug_id=chosen_drug.id,
        prescription_ref=None,
        status=order_model.STATUS_COMPLETED,
        verification_status=verify.NOT_REQUIRED,
        created_at=date.today().isoformat(),
    )

    orders.append(new_order)
    order_model.save_orders(orders)

    drugs = drug_model.load_drugs()

    for stored_drug in drugs:
        if stored_drug.id == chosen_drug.id:
            stored_drug.stock = stored_drug.stock - 1

    drug_model.save_drugs(drugs)

    print(f"Order #{new_order.id} completed: {chosen_drug.name} - {chosen_drug.price:.2f}")

    if advisory_message is not None:
        print()
        print(advisory_message)
        print("The pharmacist can see this pattern with: advisories")


@requires_role("customer")
def my_orders(args, user):
    del args

    orders = order_model.orders_for_customer(user.id)

    if not orders:
        print("You have not placed any orders yet.")
        return

    print(f"{'ID':<5} {'DRUG':<22} {'DATE':<12} {'STATUS':<11} CHECK")
    print("-" * 78)

    for order in orders:
        ordered_drug = drug_model.find_by_id(order.drug_id)
        drug_name = ordered_drug.name if ordered_drug else "unknown drug"

        print(
            f"{order.id:<5} {drug_name:<22} {order.created_at:<12} "
            f"{order.status:<11} {verify.describe(order.verification_status)}"
        )