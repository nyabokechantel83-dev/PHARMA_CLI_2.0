
import json
import re
from argon2 import PasswordHasher


class Registration:

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

        self.role = "user"

    def validate_name(self):

        name = self.name.strip()

        if not name:
            return "Name cannot be blank"

        if not re.fullmatch(r"[A-Za-z ]+", name):
            return "Name should contain only letters and spaces"

        return None

    def validate_email(self):

        email = self.email.strip()

        if not email:
            return "Email cannot be blank"

        email_pattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )

        if not re.fullmatch(email_pattern, email):
            return "Please enter a valid email address"

        return None

    def validate_password(self):

        password = self.password

        if not password:
            return "Password cannot be blank"

        if len(password) < 8:
            return "Password must be at least 8 characters"

        if not re.search(r"[A-Z]", password):
            return "Password must contain an uppercase letter"

        if not re.search(r"[a-z]", password):
            return "Password must contain a lowercase letter"

        if not re.search(r"[0-9]", password):
            return "Password must contain a number"

        if not re.search(r"[^A-Za-z0-9]", password):
            return "Password must contain a special character"

        return None

    def save_user(self):

        error = self.validate_name()

        if error:
            return error

        error = self.validate_email()

        if error:
            return error


        error = self.validate_password()

        if error:
            return error

        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)

                if not isinstance(users, list):
                    users = []

        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        email = self.email.strip().lower()

        for user in users:

            if user["email"].lower() == email:
                return "Email already registered"

        ph = PasswordHasher()
        hashed_password = ph.hash(self.password)

        new_user = {
            "name": self.name.strip(),
            "email": email,
            "password": hashed_password,
            "role": self.role
        }

        users.append(new_user)

        with open("data/users.json", "w") as file:
            json.dump(users, file, indent=4)

        return "User registered successfully"

