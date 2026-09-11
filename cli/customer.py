from utils.auth import requires_role


def register_subparser(subparser, services):
    list_parser = subparser.add_parser("list-drugs", help="List all drugs in the catalog")
    list_parser.set_defaults(func=lambda args: _list_drugs(args, services))

    show_parser = subparser.add_parser("show", help="Show a single drug's details")
    show_parser.add_argument("drug_id", help="ID of the drug to view")
    show_parser.set_defaults(func=lambda args: _show_drug(args, services))

    order_parser = subparser.add_parser("Order", help="Order a drug")
    order_parser.add_argument("drug_id", help="ID of the drug to order")
    order_parser.add_argument(
        "--prescription-ref",
        dest="prescription_ref",
        default=None,
        help="Prescription reference(required for prescription-only drugs)",
    )
    order_parser.set_defaults(func=lambda args: _place_order(args, services))


def _list_drugs(args, services):
    drugs = services.drug.list_drugs()

    if not drugs:
        print("No drugs in the catalog yet.")
        return
    
    print(f"{'ID':<10}{'Name':<20}{'Price':<10}{'Stock':<8}{'Rx?':<5}")
    for drug in drugs:
        rx_flag = "Yes" if drug.requires_prescription else "No"
        print(f"{drug.id:<10}{drug.name:<20}{drug.price:<10}{drug.Stock:<8}{rx_flag:<5}")
        

        print(drug)


def _show_drug(args, services):
    try:
        drug = services.drug.get_drug(args.drug_id)
    except ValueError as error:
        print(f"Error: {error}")
        return
    
    print(f"Name:               {drug.name}")
    print(f"Price:              {drug.price}")
    print(f"Stock:              {drug.stock}")
    print(f"Category:           {getattr(drug, 'category', 'general')}")
    print(f"Requires prescription:{'Yes' if drug.requires_prescription else 'No'}")

@requires_role("customer")
def _place_order_for_current_customer(current_customer, args, services):
    order = services.place_order(
        customer=current_customer,
        drug_id=args.drug_id,
        prescription_ref=args.prescription_ref,
    )
    if order.status == "pending":
        verification_status = services.verify.verify_prescription(
            ref=order.prescription_ref,
            drug_name=services.drug.get_drug(order.drug_id).name,
        )
        services.order.set_verification_status(order.id, verification_status)
        print(f"Order {order.id} is PENDING pharmacist review"
             (f"Verification status: {verification_status}")
        )
    else:
        print(f"Order {order.id} CONFIRMED.")

        drug = services.drug.get_drug(order.drug_id)
        advisory = services.verify.otc_advisory(
            customer_id=current_customer.id,
            category=drug.category,
        )
        if advisory:
            print(advisory)

def _place_order(args, services):
    current_user = services.auth.get_current_user()
    try:
        _place_order_for_current_customer(current_customer=current_user, args=args, services=services)
    except ValueError as error:
        print(f"Error: {error}")