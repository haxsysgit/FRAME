"""Role policy matrix smoke checks for core invoice permissions.

Run with API server active, e.g. from Backend/:

    uv run fastapi dev main.py

Then in another terminal:

    uv run python3 -m tests.test_role_policy_matrix
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from uuid import uuid4

import requests


BASE_URL = "http://127.0.0.1:8000"
PASSWORD = "test12345"


@dataclass
class Actor:
    role: str
    username: str
    token: str


def register_if_needed(*, role: str, username: str, email: str, password: str) -> None:
    resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "full_name": f"{role.title()} Matrix User",
            "password": password,
            "role": role,
        },
    )
    if resp.status_code == 201:
        return
    if resp.status_code == 400 and "already registered" in resp.text.lower():
        return
    resp.raise_for_status()


def login(*, identifier: str, password: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "identifier": identifier,
            "password": password,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def assert_route_access(*, actor: Actor, method: str, path: str, payload: dict | None, allowed: bool) -> None:
    request = getattr(requests, method.lower())
    resp = request(f"{BASE_URL}{path}", headers=auth_headers(actor.token), json=payload)

    if allowed:
        if resp.status_code in {200, 201, 400, 404, 422}:
            print(f"✅ {actor.role:7} {method:4} {path} -> {resp.status_code}")
            return
        raise AssertionError(
            f"{actor.role} should be allowed on {method} {path}, got {resp.status_code}: {resp.text[:180]}"
        )

    if resp.status_code == 403:
        print(f"✅ {actor.role:7} {method:4} {path} correctly denied (403)")
        return

    raise AssertionError(
        f"{actor.role} should be denied on {method} {path}, got {resp.status_code}: {resp.text[:180]}"
    )


def create_invoice(*, actor: Actor) -> str:
    resp = requests.post(f"{BASE_URL}/invoices/", headers=auth_headers(actor.token))
    resp.raise_for_status()
    return resp.json()["id"]


def main() -> None:
    suffix = str(uuid4())[:8]

    users = [
        ("ADMIN", f"admin_matrix_{suffix}", f"admin_matrix_{suffix}@pharmax.local"),
        ("CASHIER", f"cashier_matrix_{suffix}", f"cashier_matrix_{suffix}@pharmax.local"),
        ("STAFF", f"staff_matrix_{suffix}", f"staff_matrix_{suffix}@pharmax.local"),
    ]

    actors: Dict[str, Actor] = {}
    for role, username, email in users:
        register_if_needed(role=role, username=username, email=email, password=PASSWORD)
        token = login(identifier=username, password=PASSWORD)
        actors[role] = Actor(role=role, username=username, token=token)

    admin = actors["ADMIN"]
    cashier = actors["CASHIER"]
    staff = actors["STAFF"]

    print("\n=== Invoice route role matrix ===")

    # Route-level access matrix checks.
    assert_route_access(actor=admin, method="GET", path="/invoices/all", payload=None, allowed=True)
    assert_route_access(actor=cashier, method="GET", path="/invoices/all", payload=None, allowed=True)
    assert_route_access(actor=staff, method="GET", path="/invoices/all", payload=None, allowed=True)

    assert_route_access(actor=admin, method="POST", path="/invoices/", payload=None, allowed=True)
    assert_route_access(actor=cashier, method="POST", path="/invoices/", payload=None, allowed=True)
    assert_route_access(actor=staff, method="POST", path="/invoices/", payload=None, allowed=True)

    # Use fresh invoices so state transitions don't interfere with role checks.
    invoice_for_finalize = create_invoice(actor=staff)
    invoice_for_cancel = create_invoice(actor=staff)
    invoice_for_dispense = create_invoice(actor=staff)

    finalize_path = f"/invoices/{invoice_for_finalize}/finalize"
    finalize_payload = {"payment_method": "CASH"}
    assert_route_access(actor=admin, method="POST", path=finalize_path, payload=finalize_payload, allowed=True)
    assert_route_access(actor=cashier, method="POST", path=finalize_path, payload=finalize_payload, allowed=True)
    assert_route_access(actor=staff, method="POST", path=finalize_path, payload=finalize_payload, allowed=False)

    cancel_path = f"/invoices/{invoice_for_cancel}/cancel"
    cancel_payload = {"reason": "Customer requested cancellation"}
    assert_route_access(actor=admin, method="POST", path=cancel_path, payload=cancel_payload, allowed=True)
    assert_route_access(actor=cashier, method="POST", path=cancel_path, payload=cancel_payload, allowed=True)
    assert_route_access(actor=staff, method="POST", path=cancel_path, payload=cancel_payload, allowed=True)

    dispense_path = f"/invoices/{invoice_for_dispense}/dispense"
    assert_route_access(actor=admin, method="POST", path=dispense_path, payload=None, allowed=True)
    assert_route_access(actor=staff, method="POST", path=dispense_path, payload=None, allowed=True)
    assert_route_access(actor=cashier, method="POST", path=dispense_path, payload=None, allowed=False)

    print("\nAll role matrix checks passed.")


if __name__ == "__main__":
    main()
