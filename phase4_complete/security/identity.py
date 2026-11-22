"""Verified Streamlit OIDC identity mapped to the approved demo user registry."""
import csv
import os
from pathlib import Path

import streamlit as st
from .policy import Principal, ROLES


def resolve_principal(config_dir: Path) -> Principal:
    """Resolve the authenticated OIDC email to a pre-approved user_id.

    Production never accepts a role, department, or team from browser input.
    The email-to-user mapping is an operator-managed Streamlit secret; role and
    organisational scope are read only from the committed/approved user registry.
    """
    auth_mode = os.getenv("PULSEIQ_AUTH_MODE", "production").lower()
    if auth_mode == "production":
        if not st.user.is_logged_in:
            raise PermissionError("Sign in with the configured identity provider.")
        email = str(getattr(st.user, "email", "") or "").strip().lower()
        if not email:
            raise PermissionError("The identity provider did not return an email address.")
        try:
            mapping = st.secrets["identity"]["email_to_user_id"]
            user_id = str(mapping[email]).strip()
        except Exception as exc:
            raise PermissionError("Your signed-in account is not mapped to an approved PulseIQ demo user.") from exc
    else:
        user_id = os.getenv("PULSEIQ_DEMO_USER", "").strip()
        if not user_id:
            raise PermissionError("Set PULSEIQ_DEMO_USER to a user in config/demo_users.csv for local testing.")

    registry = config_dir / "demo_users.csv"
    if not registry.exists():
        raise FileNotFoundError(f"Approved user registry is missing: {registry}")
    with registry.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["user_id"].strip() == user_id:
                role = row["role"].strip().upper()
                if role not in ROLES:
                    break
                teams = tuple(x.strip() for x in row.get("team_ids", "").split(";") if x.strip())
                return Principal(user_id, role, row.get("department_id") or None, teams)
    raise PermissionError("The mapped user is not present in the approved demo user registry.")
