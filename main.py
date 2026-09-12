from Auth.registration import Registration
from Auth.login import Login


def register():

    print("\n===== REGISTRATION =====")

    name = input("Your name: ")
    email = input("Your email: ")
    password = input("Your password: ")

    user = Registration(
        name,
        email,
        password
    )

    result = user.save_user()

    print("\n" + result)

    if result == "User registered successfully":

        return {
            "name": user.name,
            "email": user.email,
            "role": user.role
        }

    return None


def login():

    print("\n===== LOGIN =====")

    email = input("Your email: ")
    password = input("Your password: ")

    user_login = Login(
        email,
        password
    )

    result = user_login.authenticate()

    print("\n" + result["message"])

    if result["success"]:

        user = result["user"]

        print("\nWelcome back,", user["name"])

        return user

    return None


def start_menu(user):

    while True:

        print("\n====================")
        print("      START MENU")
        print("====================")

        print("1. View profile")
        print("2. Logout")

        choice = input("Choose an option: ")

        if choice == "1":

            print("\n===== PROFILE =====")
            print("Name:", user["name"])
            print("Email:", user["email"])
            print("Role:", user["role"])

        elif choice == "2":

            print("\nLogged out successfully.")
            break

        else:

            print("Invalid option.")


def main():

    while True:

        print("\n====================")
        print("       MY APP")
        print("====================")

        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":

            user = register()

            if user:
                start_menu(user)

        elif choice == "2":

            user = login()

            if user:
                start_menu(user)

        elif choice == "3":

            print("Goodbye!")
            break

        else:

            print("Invalid option.")


main()