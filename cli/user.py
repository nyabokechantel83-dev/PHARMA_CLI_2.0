"""The User class - an account plus the role it is allowed to act as."""

from dataclasses import dataclass, asdict

from utils import storage

FILE_NAME = "users.json"

# The only three roles the program accepts.
ROLES = ["doctor", "pharmacist", "customer"]


@dataclass
class User:
    """One account in the system."""

    id: int
    name: str
    email: str
    role: str
    password_hash: str
    salt: str

    def to_dict(self):
        """Turn this object into a plain dictionary so it can be saved as JSON."""
        return asdict(self)

    @staticmethod
    def from_dict(row):
        """Build a User back from a dictionary that was read from JSON."""
        return User(**row)


def load_users():
    """Read every user from users.json."""
    rows = storage.read_json(FILE_NAME)
    return [User.from_dict(row) for row in rows]


def save_users(users):
    """Write every user back to users.json."""
    rows = [user.to_dict() for user in users]
    storage.write_json(FILE_NAME, rows)


def find_by_email(email):
    """Return the user with this email address, or None if there is none."""
    for user in load_users():
        # Email addresses are not case sensitive in real life.
        if user.email.lower() == email.lower():
            return user

    return None


def find_by_id(user_id):
    """Return the user with this id, or None if there is none."""
    for user in load_users():
        if user.id == user_id:
            return user

    return None
