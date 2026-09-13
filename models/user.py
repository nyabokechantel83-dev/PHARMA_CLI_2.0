

from dataclasses import dataclass, asdict

from utils import storage

FILE_NAME = "users.json"
ROLES = ["doctor", "pharmacist", "customer"]


@dataclass
class User:

    id: int
    name: str
    email: str
    role: str
    password_hash: str
    salt: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(row):
        return User(**row)


def load_users():
    rows = storage.read_json(FILE_NAME)
    return [User.from_dict(row) for row in rows]


def save_users(users):
    rows = [user.to_dict() for user in users]
    storage.write_json(FILE_NAME, rows)


def find_by_email(email):
    for user in load_users():
        if user.email.lower() == email.lower():
            return user

    return None


def find_by_id(user_id):
    for user in load_users():
        if user.id == user_id:
            return user

    return None
