import pytest
import json
import os
from Auth.login import Login
from argon2 import PasswordHasher




def create_dummy_user_file():

    if not os.path.exists("data"):
        os.makedirs("data")
    

    ph = PasswordHasher()
    hashed = ph.hash("Password123!")
    
    users = [{"email": "test@mail.com", "password": hashed}]
    
    with open("data/user.json", "w") as f:
        json.dump(users, f)


def test_login_with_empty_email():
    login = Login("", "Password123!")
    result = login.authenticate()
    assert result["success"] is False
    assert result["message"] == "Email cannot be blank"

def test_login_success():

    create_dummy_user_file()
    
    login = Login("test@mail.com", "Password123!")
    result = login.authenticate()
    
    assert result["success"] is True
    assert result["message"] == "Login successful"
    
    if os.path.exists("data/user.json"):
        os.remove("data/user.json")

def test_login_wrong_password():
    create_dummy_user_file()
    
    login = Login("test@mail.com", "WrongPassword!")
    result = login.authenticate()
    
    assert result["success"] is False
    assert result["message"] == "Incorrect email or password"
    
    if os.path.exists("data/user.json"):
        os.remove("data/user.json")