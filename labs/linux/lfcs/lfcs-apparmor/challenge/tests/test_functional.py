"""Tests pytest+testinfra — lfcs-apparmor.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT AppArmor : le module actif avec des profils chargés, et le
profil ping bien en mode complain.
"""
from __future__ import annotations

import json

import pytest

from conftest import lab_host

TARGET_HOST = "ubuntu-lfcs-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _status(host) -> dict:
    return json.loads(host.check_output("aa-status --json"))


def test_apparmor_active(host):
    """AppArmor doit être actif avec des profils chargés."""
    profiles = _status(host).get("profiles", {})
    assert profiles, (
        "AppArmor doit être actif avec des profils chargés (aa-status)."
    )


def test_ping_profile_complain(host):
    """Le profil ping doit être en mode complain."""
    profiles = _status(host).get("profiles", {})
    mode = profiles.get("ping")
    assert mode == "complain", (
        f"Le profil ping doit être en complain (vu : {mode!r}). "
        "sudo aa-complain /etc/apparmor.d/bin.ping"
    )
