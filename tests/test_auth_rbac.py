"""
SkillSprint AI - Automated Test Suite: Authentication & Role-Based Access Control
Theme: OnboardVerse | Category: Generative AI PowerPlay
"""

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_unauthenticated_user_redirected_from_protected_dashboard(client):
    res = client.get("/dashboard")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_fast_login_authenticates_admin_successfully(client):
    res = client.post("/fast-login", data={"role_name": "Administrator"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Marcus Vance" in res.data or b"Administrator" in res.data


def test_employee_forbidden_from_reviewer_decision_endpoint(client):
    # Log in as Employee
    client.post("/fast-login", data={"role_name": "Employee"}, follow_redirects=True)

    # Attempt to submit review decision
    res = client.post("/api/review/REV-TEST/decision", json={"action": "Approve", "comments": "Override"})
    assert res.status_code == 403
