"""Tests pytest+testinfra — l4-network-static-persist.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la connexion NetworkManager est en manual avec la bonne
adresse, le profil est sur disque (persistance reboot) et l'adresse est active
sur lab0 — sans jamais toucher l'interface de gestion.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
CONN = "lab-static"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_method_is_manual(host):
    """La connexion doit être en IPv4 manual (statique)."""
    method = host.check_output("nmcli -g ipv4.method con show %s", CONN).strip()
    assert method == "manual", (
        f"ipv4.method attendu 'manual' (vu : {method!r}). "
        "nmcli con add ... ipv4.method manual"
    )


def test_static_address(host):
    """L'adresse statique 192.0.2.50/24 doit être configurée."""
    addrs = host.check_output("nmcli -g ipv4.addresses con show %s", CONN).strip()
    assert "192.0.2.50/24" in addrs, (
        f"ipv4.addresses doit contenir 192.0.2.50/24 (vu : {addrs!r})."
    )


def test_profile_persisted_on_disk(host):
    """Le profil doit être sur disque (sinon perdu au reboot)."""
    profile = host.file(
        "/etc/NetworkManager/system-connections/lab-static.nmconnection"
    )
    assert profile.exists, (
        "Le profil /etc/NetworkManager/system-connections/lab-static.nmconnection "
        "doit exister (persistance reboot)."
    )


def test_address_is_live(host):
    """L'adresse doit être active sur lab0."""
    out = host.check_output("ip -4 addr show lab0")
    assert "192.0.2.50" in out, (
        f"lab0 doit porter 192.0.2.50 en live. Actif : nmcli con up {CONN}"
    )
