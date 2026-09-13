

import pytest

from utils import auth


def test_the_same_password_gives_different_hashes_for_different_salts():
    first = auth.hash_password("secret123", "salt-one")
    second = auth.hash_password("secret123", "salt-two")

    assert first != second


def test_the_real_password_is_never_stored(customer_user):
    assert "secret123" not in customer_user.password_hash


def test_check_password_accepts_the_right_password(customer_user):
    assert auth.check_password("secret123", customer_user.salt, customer_user.password_hash)


def test_check_password_refuses_the_wrong_password(customer_user):
    assert not auth.check_password("wrong", customer_user.salt, customer_user.password_hash)


def test_an_email_cannot_be_used_twice(customer_user):
    with pytest.raises(ValueError):
        auth.register("Someone Else", customer_user.email, "secret123", "customer")


def test_an_unknown_role_is_refused():
    with pytest.raises(ValueError):
        auth.register("Ann", "ann2@mail.com", "secret123", "chemist")


def test_a_short_password_is_refused():
    with pytest.raises(ValueError):
        auth.register("Ann", "ann3@mail.com", "abc", "customer")


def test_login_with_the_wrong_password_fails(customer_user):
    with pytest.raises(ValueError):
        auth.login(customer_user.email, "not-the-password")


def test_nobody_is_logged_in_at_the_start():
    assert auth.current_user() is None


def test_login_then_logout(customer_user):
    auth.login(customer_user.email, "secret123")
    assert auth.current_user().id == customer_user.id

    auth.logout()
    assert auth.current_user() is None


def test_requires_role_blocks_a_visitor_who_is_not_logged_in():

    @auth.requires_role("pharmacist")
    def protected_command(args, user):
        return "ran"

    with pytest.raises(PermissionError):
        protected_command(args=None)


def test_requires_role_blocks_the_wrong_role(customer_user):
    auth.login(customer_user.email, "secret123")

    @auth.requires_role("pharmacist")
    def protected_command(args, user):
        return "ran"

    with pytest.raises(PermissionError):
        protected_command(args=None)


def test_requires_role_lets_the_right_role_through(pharmacist_user):
    auth.login(pharmacist_user.email, "secret123")

    @auth.requires_role("pharmacist")
    def protected_command(args, user):
        return user.name

    assert protected_command(args=None) == "Pam Pharm"
