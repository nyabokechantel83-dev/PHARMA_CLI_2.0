"""
Tests for utils/auth.py — the @requires_role decorator that enforces RBAC.

Plain-English summary:
- @requires_role("pharmacist") should let a pharmacist through.
- It should BLOCK a customer (or anyone with the wrong role) and
  raise a PermissionError instead of running the function.
- This one decorator is what protects add-drug, claims, decide,
  and issue-prescription across the whole app.
"""

import pytest

from utils.auth import requires_role, PermissionError as RolePermissionError


def test_requires_role_allows_the_matching_role(pharmacist):
    
    @requires_role("pharmacist")
    def restock_shelf(current_user):
        return "shelf restocked"

    result = restock_shelf(current_user=pharmacist)

    assert result == "shelf restocked"


def test_requires_role_blocks_the_wrong_role(customer):
    @requires_role("pharmacist")
    def restock_shelf(current_user):
        return "shelf restocked"

    with pytest.raises(RolePermissionError):
        restock_shelf(current_user=customer)


def test_requires_role_works_for_doctor_only_actions(doctor, customer):
    @requires_role("doctor")
    def write_prescription(current_user):
        return "prescription written"

    
    assert write_prescription(current_user=doctor) == "prescription written"

    with pytest.raises(RolePermissionError):
        write_prescription(current_user=customer)
auth.test