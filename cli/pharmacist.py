from datetime import date, timedelta

from models import drug as drug_model
from models import order as order_model
from models import prescription as prescription_model
from models import user as user_model
from models.drug import Drug
from utils import storage, verify
from utils.auth import requires_role


def add_commands(subparsers):
    add_parser = subparsers.add_parser("add-drug", help="[pharmacist] Add a drug to the inventory")
    add_parser.add_argument("--name", required=True, help="Name of the drug")
    add_parser.add_argument("--price", type=float, required=True, help="Price per unit")
    add_parser.add_argument("--stock", type=int, required=True, help="How many units are in stock")
    add_parser.add_argument(
        "--category",
        default="general",
        help="Category, for example painkiller or antibiotic",
    )
    add_parser.add_argument(
        "--requires-rx",
        action="store_true",
        help="Add this flag if the drug needs a prescription",
    )
    add_parser.set_defaults(func=add_drug)

    restock_parser = subparsers.add_parser("restock", help="[pharmacist] Add stock to a drug")
    restock_parser.add_argument("--drug-id", type=int, required=True, help="Id of the drug")
    restock_parser.add_argument("--amount", type=int, required=True, help="Units to add")
    restock_parser.set_defaults(func=restock)

    list_parser = subparsers.add_parser("list-drugs", help="[pharmacist] Show the whole inventory")
    list_parser.set_defaults(func=list_drugs)

    claims_parser = subparsers.add_parser(
        "list-claims",
        help="[pharmacist] Show the orders waiting for a decision",
    )
    claims_parser.set_defaults(func=list_claims)

    decide_parser = subparsers.add_parser(
        "decide",
        help="[pharmacist] Approve or reject a waiting claim",
    )
    decide_parser.add_argument("--order-id", type=int, required=True, help="Id of the order")
    decision_group = decide_parser.add_mutually_exclusive_group(required=True)
    decision_group.add_argument("--approve", action="store_true", help="Approve the claim")
    decision_group.add_argument("--reject", action="store_true", help="Reject the claim")
    decide_parser.set_defaults(func=decide)

    advisories_parser = subparsers.add_parser(
        "advisories",
        help="[pharmacist] Show over the counter purchases worth a second look",
    )
    advisories_parser.set_defaults(func=advisories)


@requires_role("pharmacist")
def add_drug(args, user):
    del user

    if args.price < 0:
        raise ValueError("--price cannot be negative.")

    if args.stock < 0:
        raise ValueError("--stock cannot be negative.")

    drugs = drug_model.load_drugs()

    new_drug = Drug(
        id=storage.next_id(drugs),
        name=args.name,
        price=args.price,
        stock=args.stock,
        category=args.category,
        requires_rx=args.requires_rx,
    )

    drugs.append(new_drug)
    drug_model.save_drugs(drugs)

    rx_text = "prescription required" if new_drug.requires_rx else "over the counter"
    print(f"Added #{new_drug.id} {new_drug.name} ({rx_text})")
    print(f"  Price: {new_drug.price:.2f}   Stock: {new_drug.stock}")


@requires_role("pharmacist")
def restock(args, user):
    del user

    if args.amount < 1:
        raise ValueError("--amount must be at least 1.")

    drugs = drug_model.load_drugs()

    for stored_drug in drugs:
        if stored_drug.id == args.drug_id:
            stored_drug.stock = stored_drug.stock + args.amount
            drug_model.save_drugs(drugs)
            print(f"{stored_drug.name} restocked. New stock: {stored_drug.stock}")
            return

    raise ValueError(f"There is no drug with id {args.drug_id}.")


@requires_role("pharmacist")
def list_drugs(args, user):
    del args, user

    drugs = drug_model.load_drugs()

    if not drugs:
        print("The inventory is empty. Add a drug with: add-drug ...")
        return

    print(f"{'ID':<5} {'NAME':<22} {'CATEGORY':<14} {'PRICE':>8} {'STOCK':>6}  TYPE")
    print("-" * 76)

    for stored_drug in drugs:
        rx_text = "Rx" if stored_drug.requires_rx else "OTC"
        print(
            f"{stored_drug.id:<5} {stored_drug.name:<22} {stored_drug.category:<14} "
            f"{stored_drug.price:>8.2f} {stored_drug.stock:>6}  {rx_text}"
        )


@requires_role("pharmacist")
def list_claims(args, user):
    del args, user

    waiting = [
        order
        for order in order_model.load_orders()
        if order.status == order_model.STATUS_PENDING
    ]

    if not waiting:
        print("No claims are waiting for a decision.")
        return

    for order in waiting:
        customer = user_model.find_by_id(order.customer_id)
        ordered_drug = drug_model.find_by_id(order.drug_id)

        customer_name = customer.name if customer else "unknown customer"
        drug_name = ordered_drug.name if ordered_drug else "unknown drug"

        print(f"Claim #{order.id}   placed {order.created_at}")
        print(f"  Customer     : {customer_name}")
        print(f"  Drug         : {drug_name}")
        print(f"  Prescription : {order.prescription_ref}")
        print(f"  Check        : {verify.describe(order.verification_status)}")
        print(f"  Decide with  : decide --order-id {order.id} --approve")
        print()


@requires_role("pharmacist")
def decide(args, user):
    del user

    orders = order_model.load_orders()
    chosen_order = None

    for stored_order in orders:
        if stored_order.id == args.order_id:
            chosen_order = stored_order
            break

    if chosen_order is None:
        raise ValueError(f"There is no order with id {args.order_id}.")

    if chosen_order.status != order_model.STATUS_PENDING:
        raise ValueError(
            f"Order #{chosen_order.id} was already decided (status: {chosen_order.status})."
        )

    if args.reject:
        chosen_order.status = order_model.STATUS_REJECTED
        order_model.save_orders(orders)
        print(f"Claim #{chosen_order.id} rejected. No stock was taken.")
        return

    if chosen_order.verification_status != verify.VERIFIED:
        print("WARNING: this claim did not pass the automatic check.")
        print(f"         {verify.describe(chosen_order.verification_status)}")
        print()

    drugs = drug_model.load_drugs()
    ordered_drug = None

    for stored_drug in drugs:
        if stored_drug.id == chosen_order.drug_id:
            ordered_drug = stored_drug
            break

    if ordered_drug is None:
        raise ValueError("The drug on this order is no longer in the inventory.")

    if ordered_drug.stock < 1:
        raise ValueError(f"{ordered_drug.name} is out of stock. Restock before approving.")

    ordered_drug.stock = ordered_drug.stock - 1
    drug_model.save_drugs(drugs)

    chosen_order.status = order_model.STATUS_APPROVED
    order_model.save_orders(orders)

    mark_prescription_used(chosen_order.prescription_ref)

    print(f"Claim #{chosen_order.id} approved.")
    print(f"  {ordered_drug.name} dispensed. Stock left: {ordered_drug.stock}")
    print(f"  Prescription {chosen_order.prescription_ref} is now marked as used.")


@requires_role("pharmacist")
def advisories(args, user):
    del args, user

    today = date.today()
    window_starts = today - timedelta(days=verify.ADVISORY_DAYS)

    counts = {}

    for order in order_model.load_orders():
        if order.status == order_model.STATUS_REJECTED:
            continue

        if date.fromisoformat(order.created_at) < window_starts:
            continue

        key = (order.customer_id, order.drug_id)
        counts[key] = counts.get(key, 0) + 1

    something_to_report = False

    for (customer_id, drug_id), times_bought in counts.items():
        if times_bought < verify.ADVISORY_LIMIT:
            continue

        bought_drug = drug_model.find_by_id(drug_id)

        if bought_drug is None or bought_drug.requires_rx:
            continue

        customer = user_model.find_by_id(customer_id)
        customer_name = customer.name if customer else "unknown customer"

        print(
            f"{customer_name} bought {bought_drug.name} {times_bought} times "
            f"in the last {verify.ADVISORY_DAYS} days."
        )
        something_to_report = True

    if not something_to_report:
        print("Nothing to flag. No repeated over the counter purchases.")


def mark_prescription_used(ref):
    if ref is None:
        return

    prescriptions = prescription_model.load_prescriptions()

    for stored_prescription in prescriptions:
        if stored_prescription.ref.upper() == ref.upper():
            stored_prescription.used = True
            prescription_model.save_prescriptions(prescriptions)
            return