"""Tests pytest+testinfra — l4-network-troubleshoot.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la connexion est active, auto-connectable (persistance
reboot) et l'adresse est présente sur lab1 — sans toucher la gestion.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"
CONN = "lab-net"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_connection_activated(host):
    """La connexion doit être active."""
    state = host.check_output("nmcli -g GENERAL.STATE con show %s", CONN).strip()
    assert state == "activated", message(
        en=f"lab-net must be 'activated' (seen: {state!r}). nmcli con up {CONN}",
        fr=f"lab-net doit être 'activated' (vu : {state!r}). nmcli con up {CONN}",
    )


def test_autoconnect_enabled(host):
    """autoconnect doit être yes (persistance reboot)."""
    ac = host.check_output(
        "nmcli -g connection.autoconnect con show %s", CONN
    ).strip()
    assert ac == "yes", message(
        en=f"connection.autoconnect 'yes' expected (seen: {ac!r}), otherwise the connection "
        f"does not come back at reboot. nmcli con mod {CONN} connection.autoconnect yes",
        fr=f"connection.autoconnect attendu 'yes' (vu : {ac!r}), sinon la connexion "
        f"ne remonte pas au reboot. nmcli con mod {CONN} connection.autoconnect yes",
    )


def test_address_is_live(host):
    """L'adresse doit être active sur lab1."""
    out = host.check_output("ip -4 addr show lab1")
    assert "198.51.100.10" in out, message(
        en="lab1 must carry 198.51.100.10 live.",
        fr="lab1 doit porter 198.51.100.10 en live.",
    )
