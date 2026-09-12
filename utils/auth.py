
import functools
import hashlib
import json
import secrets

from models import user as user_model
from models.user import ROLES, User
from utils import storage

SESSION_FILE = "session.json"
HASH_ROUNDS = 100_000

def hash_password(password, salt):

    raw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ROUNDS,
    )
    return raw_hash.hex()


def check_password(password, salt, expected_hash):
    actual_hash = hash_password(password, salt)

    return secrets.compare_digest(actual_hash, expected_hash)


def register(name, email, password, role):
 
    if role not in ROLES:
        raise ValueError(f"Role must be one of: {', '.join(ROLES)}")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    if user_model.find_by_email(email) is not None:
        raise ValueError(f"An account already uses the email {email}.")

    users = user_model.load_users()
    salt = secrets.token_hex(16)

    new_user = User(
        id=storage.next_id(users),
        name=name,
        email=email,
        role=role,
        password_hash=hash_password(password, salt),
        salt=salt,
    )

    users.append(new_user)
    user_model.save_users(users)

    return new_user


def login(email, password):

    found_user = user_model.find_by_email(email)


    if found_user is None:
        raise ValueError("Email or password is not correct.")

    if not check_password(password, found_user.salt, found_user.password_hash):
        raise ValueError("Email or password is not correct.")

    _write_session(found_user)
    return found_user


def logout():
    path = storage.DATA_DIR / SESSION_FILE

    if not path.exists():
        return False

    path.unlink()
    return True


def current_user():
    path = storage.DATA_DIR / SESSION_FILE

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        session = json.load(file)

    return user_model.find_by_id(session["user_id"])


def _write_session(logged_in_user):

    session = {
        "user_id": logged_in_user.id,
        "token": secrets.token_hex(16),
    }

    path = storage.DATA_DIR / SESSION_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(session, file, indent=2)

def requires_role(role):
   
    def decorator(command_function):

        @functools.wraps(command_function)
        def wrapper(args):
            logged_in_user = current_user()

            if logged_in_user is None:
                raise PermissionError(
                    "You are not logged in. Run: python main.py login --email ... --password ..."
                )

            if logged_in_user.role != role:
                raise PermissionError(
                    f"Only a {role} can run this command. "
                    f"You are logged in as a {logged_in_user.role}."
                )

            return command_function(args, logged_in_user)

        return wrapper

    return decorator
