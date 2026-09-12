import pytest

from Auth.registration import Registration 



def test_name_validation():

    user = Registration("", "test@mail.com", "Password123!")
    assert user.validate_name() == "Name cannot be blank"

def test_password_too_short():

    user = Registration("John", "test@mail.com", "123")
    assert user.validate_password() == "Password must be at least 8 characters"

def test_email_invalid():

    user = Registration("John", "bad-email", "Password123!")
    assert user.validate_email() == "Please enter a valid email address"

def test_registration_stops_on_bad_data():
    
    user = Registration("John", "john@mail.com", "short")
    result = user.save_user()
    
    assert result == "Password must be at least 8 characters"