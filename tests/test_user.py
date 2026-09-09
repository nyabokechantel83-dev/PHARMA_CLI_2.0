"""
Tests for models/user.py — registering an account and logging in.

Plain-English summary of what "should" happen:
- Anyone can register with a name, email, password, and a role.
- Once registered, they can log in with the same email + password.
- Wrong password should NOT let them in.
- Two users can't share the same email.
"""

import pytest

from models.user import register, login


def test_register_creates_a_user_with_the_given_role():
    
    user = register(
        name="Joey",
        email="joey@example.com",
        password="Str0ngPass!",
        role="customer",
    )

    assert user.name == "Joey"
    assert user.email == "joey@example.com"
    assert user.role == "customer"


def test_register_does_not_store_the_plain_password():
    
    user = register(
        name="Joey",
        email="joey@example.com",
        password="Str0ngPass!",
        role="customer",
    )

    assert user.password_hash != "Str0ngPass!"


def test_register_rejects_a_duplicate_email():
    
    register(name="Joey", email="joey@example.com", password="pass1", role="customer")

    with pytest.raises(ValueError):
        register(name="Joey Two", email="joey@example.com", password="pass2", role="customer")


def test_login_succeeds_with_correct_credentials():
    register(name="Joey", email="joey@example.com", password="Str0ngPass!", role="customer")

    user = login(email="joey@example.com", password="Str0ngPass!")

    assert user.email == "joey@example.com"


def test_login_fails_with_wrong_password():
    register(name="Joey", email="joey@example.com", password="Str0ngPass!", role="customer")

    with pytest.raises(ValueError):
        login(email="joey@example.com", password="WrongPassword")


def test_login_fails_for_an_email_that_was_never_registered():
    with pytest.raises(ValueError):
        login(email="ghost@example.com", password="whatever")
user.test