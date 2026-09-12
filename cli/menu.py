import getpass
from argparse import Namespace

from cli import customer, doctor, pharmacist
from models.user import ROLES
from utils import auth


def run():
    print()
    print("=== Pharma-CLI ===")
    print("Pharmacy order management with prescription verification.")

    while True:
        print()
        logged_in_user = auth.current_user()

        try:
            if logged_in_user is None:
                keep_going = logged_out_menu()
            else:
                keep_going = logged_in_menu(logged_in_user)

        except (EOFError, KeyboardInterrupt):
            print()
            print("Goodbye.")
            return 0

        except ValueError as error:
            print(f"Error: {error}")
            keep_going = True

        except PermissionError as error:
            print(f"Permission denied: {error}")
            keep_going = True

        if not keep_going:
            print("Goodbye.")
            return 0

def logged_out_menu():
    print("Nobody is logged in.")
    print()

    choice = ask_choice(["Register", "Login", "Quit"])

    if choice == 1:
        do_register()
    elif choice == 2:
        do_login()
    else:
        return False

    return True


def logged_in_menu(logged_in_user):
    print(f"Logged in as {logged_in_user.name} ({logged_in_user.role}).")
    print()

    if logged_in_user.role == "doctor":
        return doctor_menu()

    if logged_in_user.role == "pharmacist":
        return pharmacist_menu()

    return customer_menu()


def doctor_menu():
    choice = ask_choice([
        "Write a prescription",
        "See the prescriptions I have written",
        "Log out",
        "Quit",
    ])

    if choice == 1:
        doctor.issue_prescription(Namespace(
            patient_name=ask_text("Patient full name"),
            drug_name=ask_text("Drug name"),
            days_valid=ask_whole_number("How many days is it valid for", default=30),
        ))

    elif choice == 2:
        doctor.list_prescriptions(Namespace())

    elif choice == 3:
        do_logout()

    else:
        return False

    return True


def pharmacist_menu():
    choice = ask_choice([
        "Add a drug",
        "Restock a drug",
        "List drugs",
        "Review claims",
        "Advisories",
        "Log out",
        "Quit",
    ])

    if choice == 1:
        pharmacist.add_drug(Namespace(
            name=ask_text("Drug name"),
            price=ask_decimal("Price"),
            stock=ask_whole_number("Stock"),
            category=ask_text("Category", default="general"),
            requires_rx=ask_yes_no("Does it need a prescription?"),
        ))

    elif choice == 2:
        pharmacist.list_drugs(Namespace())
        pharmacist.restock(Namespace(
            drug_id=ask_whole_number("Id of the drug to restock"),
            amount=ask_whole_number("How many units to add"),
        ))

    elif choice == 3:
        pharmacist.list_drugs(Namespace())

    elif choice == 4:
        review_claims()

    elif choice == 5:
        pharmacist.advisories(Namespace())

    elif choice == 6:
        do_logout()

    else:
        return False

    return True


def customer_menu():
    choice = ask_choice([
        "Browse the drugs on sale",
        "Place an order",
        "See my orders",
        "Log out",
        "Quit",
    ])

    if choice == 1:
        customer.browse(Namespace())

    elif choice == 2:
        place_an_order()

    elif choice == 3:
        customer.my_orders(Namespace())

    elif choice == 4:
        do_logout()

    else:
        return False

    return True

def review_claims():
    pharmacist.list_claims(Namespace())

    if not ask_yes_no("Decide on a claim now?"):
        return

    claim_id = ask_whole_number("Claim id")
    approve = ask_yes_no("Approve it? (answering n rejects it)")

    pharmacist.decide(Namespace(
        order_id=claim_id,
        approve=approve,
        reject=not approve,
    ))


def place_an_order():
    customer.browse(Namespace())

    drug_id = ask_whole_number("Id of the drug you want")
    reference = ask_optional_text(
        "Prescription reference (press Enter if the drug does not need one)"
    )

    customer.place_order(Namespace(
        drug_id=drug_id,
        prescription_ref=reference,
    ))


def do_register():
    name = ask_text("Full name")
    email = ask_text("Email")
    password = ask_new_password()
    role = ask_role()

    new_user = auth.register(name, email, password, role)

    print(f"Account created for {new_user.name} ({new_user.role}).")
    print("Choose Login to sign in.")


def do_login():
    email = ask_text("Email")
    password = ask_password()

    logged_in_user = auth.login(email, password)

    print(f"Logged in as {logged_in_user.name} ({logged_in_user.role}).")


def do_logout():
    auth.logout()
    print("Logged out.")

def ask_text(question, default=None):
    while True:
        if default is None:
            answer = input(f"{question}: ").strip()
        else:
            answer = input(f"{question} [{default}]: ").strip()
            if answer == "":
                return default

        if answer != "":
            return answer

        print("  Please type something.")


def ask_optional_text(question):
    answer = input(f"{question}: ").strip()

    if answer == "":
        return None

    return answer


def ask_whole_number(question, default=None):
    while True:
        if default is None:
            answer = input(f"{question}: ").strip()
        else:
            answer = input(f"{question} [{default}]: ").strip()
            if answer == "":
                return default

        try:
            return int(answer)
        except ValueError:
            print("  Please type a whole number, for example 10.")


def ask_decimal(question):
    while True:
        answer = input(f"{question}: ").strip()

        try:
            return float(answer)
        except ValueError:
            print("  Please type a number, for example 50 or 49.99.")


def ask_yes_no(question):
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print("  Please answer y or n.")


def ask_choice(options):
    for number, option in enumerate(options, start=1):
        print(f"  {number}. {option}")

    print()

    while True:
        answer = input("Choose: ").strip()

        try:
            chosen = int(answer)
        except ValueError:
            print("  Please type the number next to the option you want.")
            continue

        if 1 <= chosen <= len(options):
            return chosen

        print(f"  Please type a number between 1 and {len(options)}.")


def ask_role():
    print()
    print("Which role is this account for?")
    chosen = ask_choice(ROLES)

    return ROLES[chosen - 1]


def ask_password(question="Password"):
    return getpass.getpass(f"{question}: ")


def ask_new_password():
    while True:
        password = ask_password()
        again = ask_password("Type it again")

        if password == again:
            return password

        print("  Those two did not match. Try again.")