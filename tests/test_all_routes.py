import pytest
from app import app
from src.database.db import query_one

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_public_routes(client):
    res_home = client.get("/")
    assert res_home.status_code == 200

    res_login = client.get("/login")
    assert res_login.status_code == 200

def test_authenticated_admin_routes(client):
    # Log in as Administrator using fast-login
    login_res = client.post("/fast-login", data={"role_name": "Administrator"}, follow_redirects=True)
    assert login_res.status_code == 200

    plan_row = query_one("SELECT plan_id FROM onboarding_plans LIMIT 1")
    plan_id = plan_row["plan_id"] if plan_row else "PLAN-AV-ENG-001"

    emp_row = query_one("SELECT employee_id FROM employees LIMIT 1")
    emp_id = emp_row["employee_id"] if emp_row else "EMP-001"

    endpoints = [
        "/dashboard",
        "/documents",
        "/matrix",
        "/employees",
        f"/onboarding/generate/{emp_id}",
        f"/onboarding/plan/{plan_id}",
        f"/onboarding/plan/{plan_id}/comparison",
        "/review-queue",
        "/reports",
        "/security-tests"
    ]

    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Endpoint {ep} returned status {res.status_code}"
