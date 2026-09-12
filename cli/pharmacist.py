from types import SimpleNamespace
from models import drug as drug_model
from models import order as order_model
from models import prescription as prescription_model
from utils import storage,verify
from utils.auth import requires_role
from models.drug import Drug

def add_commands(subparsers):
    add_parser=subparsers.add_parser("add-drug",help="[pharmacist] Add a drug")
    add_parser.add_argument("--name",required=True)
    add_parser.add_argument("--price",type=float,required=True)
    add_parser.add_argument("--stock",type=int,required=True)
    add_parser.add_argument("--category",default=None)
    add_parser.add_argument("--requires-rx",action="store_true")
    add_parser.set_defaults(func=add_drug)

    restock_parser=subparsers.add_parser("restock",help="[pharmacist] Restock a drug")
    restock_parser.add_argument("--drug-id",type=int,required=True)
    restock_parser.add_argument("--amount",type=int,required=True)
    restock_parser.set_defaults(func=restock)

    list_parser=subparsers.add_parser("list-drugs",help="[pharmacist] List drugs")
    list_parser.set_defaults(func=list_drugs)

    decide_parser=subparsers.add_parser("decide",help="[pharmacist] Approve or reject an order")
    decide_parser.add_argument("--order-id",type=int,required=True)
    group=decide_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--approve",action="store_true")
    group.add_argument("--reject",action="store_true")
    decide_parser.set_defaults(func=decide)

@requires_role("pharmacist")
def add_drug(args,user):
    del user

    if args.price<=0:
        raise ValueError("Price must be greater than 0")

    if args.stock<=0:
        raise ValueError("Stock must be greater than 0")

    drugs=drug_model.load_drugs()
    drug_id=storage.next_id(drugs)

    drug=Drug(
        id=drug_id,
        name=args.name,
        price=args.price,
        stock=args.stock,
        category=args.category,
        requires_prescription=args.requires_rx
    )

    drugs.append(drug)
    drug_model.save_drugs(drugs)

    print(f"Drug added: {drug.name}")

@requires_role("pharmacist")
def restock(args,user):
    del user

    if args.amount<=0:
        raise ValueError("Restock amount must be greater than 0")

    drugs=drug_model.load_drugs()

    for drug in drugs:
        drug_id=getattr(drug,"id",None)

        if str(drug_id)==str(args.drug_id):
            drug.stock+=args.amount
            drug_model.save_drugs(drugs)
            print(f"Stock updated: {drug.name} now has {drug.stock} units")
            return

    raise ValueError("Drug not found")

@requires_role("pharmacist")
def list_drugs(args,user):
    del args,user

    drugs=drug_model.load_drugs()

    if not drugs:
        print("No drugs found")
        return

    for drug in drugs:
        requires_rx="yes" if drug.requires_prescription else "no"
        print(f"{drug.id}: {drug.name} | Price: {drug.price} | Stock: {drug.stock} | Prescription: {requires_rx}")

@requires_role("pharmacist")
def decide(args,user):
    del user

    orders=order_model.load_orders()
    order=None

    for item in orders:
        if str(getattr(item,"id",None))==str(args.order_id):
            order=item
            break

    if order is None:
        raise ValueError("Order not found")

    if getattr(order,"status",None) in ("approved","rejected"):
        raise ValueError("Order has already been decided")

    if args.reject:
        order.status="rejected"
        order_model.save_orders(orders)
        print(f"Order {order.id} rejected")
        return

    drugs=drug_model.load_drugs()
    drug=None

    for item in drugs:
        if str(getattr(item,"id",None))==str(getattr(order,"drug_id",None)):
            drug=item
            break

    if drug is None:
        raise ValueError("Drug not found")

    if getattr(drug,"stock",0)<=0:
        raise ValueError("Drug is out of stock")

    verification_status=getattr(order,"verification_status",None)

    if verification_status!=verify.VERIFIED:
        print(verify.describe(verification_status))

    drug.stock-=1
    order.status="approved"

    drug_model.save_drugs(drugs)
    order_model.save_orders(orders)

    prescription_ref=getattr(order,"prescription_ref",None)

    if prescription_ref:
        prescriptions=prescription_model.load_prescriptions()

        for prescription in prescriptions:
            if prescription.ref.upper()==prescription_ref.upper():
                prescription.used=True
                break

        prescription_model.save_prescriptions(prescriptions)

    print(f"Order {order.id} approved")