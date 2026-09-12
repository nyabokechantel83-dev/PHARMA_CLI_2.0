
import json
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Login:

    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.ph = PasswordHasher()

    def authenticate(self):


        if not self.email.strip():
            return {
                "success": False,
                "message": "Email cannot be blank"
            }

        if not self.password:
            return {
                "success": False,
                "message": "Password cannot be blank"
            }

        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)

        except FileNotFoundError:
            return {
                "success": False,
                "message": "No users registered yet"
            }

        except json.JSONDecodeError:
            return {
                "success": False,
                "message": "User database is invalid"
            }

        email = self.email.strip().lower()


        for user in users:

            if user["email"].lower() == email:

                try:

                    self.ph.verify(
                        user["password"],
                        self.password
                    )

                    return {
                        "success": True,
                        "message": "Login successful",
                        "user": user
                    }

                except VerifyMismatchError:

                    return {
                        "success": False,
                        "message": "Incorrect email or password"
                    }

        return {
            "success": False,
            "message": "Incorrect email or password"
        }
