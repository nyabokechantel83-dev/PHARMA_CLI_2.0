
import argparse
import sys

from cli import customer, doctor, menu, pharmacist
from utils import auth
from models.user import ROLES

VERSION = "0.1.0"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pharma",
        description="Pharmacy order management CLI with prescription verification.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"pharma-cli {VERSION}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_account_commands(subparsers)

    doctor.add_commands(subparsers)
    pharmacist.add_commands(subparsers)
    customer.add_commands(subparsers)

    return parser

def add_account_commands(subparsers):
    register_parser = subparsers.add_parser("register", help="Create a new account")
    register_parser.add_argument("--name", required=True, help="Your full name")
    register_parser.add_argument("--email", required=True, help="Your email address")
    register_parser.add_argument("--password", required=True, help="At least 6 characters")
    register_parser.add_argument(
        "--role",
        required=True,
        choices=ROLES,
        help="Which role this account acts as",
    )
    register_parser.set_defaults(func=register_command)

    login_parser = subparsers.add_parser("login", help="Log in")
    login_parser.add_argument("--email", required=True, help="Your email address")
    login_parser.add_argument("--password", required=True, help="Your password")
    login_parser.set_defaults(func=login_command)

    logout_parser = subparsers.add_parser("logout", help="Log out")
    logout_parser.set_defaults(func=logout_command)

    whoami_parser = subparsers.add_parser("whoami", help="Show who is logged in")
    whoami_parser.set_defaults(func=whoami_command)


def register_command(args):
    new_user = auth.register(args.name, args.email, args.password, args.role)
    print(f"Account created for {new_user.name} ({new_user.role}).")
    print("Now log in with: python main.py login --email ... --password ...")


def login_command(args):
    logged_in_user = auth.login(args.email, args.password)
    print(f"Logged in as {logged_in_user.name} ({logged_in_user.role}).")


def logout_command(args):
    del args

    if auth.logout():
        print("Logged out.")
    else:
        print("Nobody was logged in.")


def whoami_command(args):
    del args

    logged_in_user = auth.current_user()

    if logged_in_user is None:
        print("Nobody is logged in.")
        return

    print(f"{logged_in_user.name} <{logged_in_user.email}> - role: {logged_in_user.role}")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return menu.run()

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        args.func(args)
    except PermissionError as error:
        print(f"Permission denied: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
