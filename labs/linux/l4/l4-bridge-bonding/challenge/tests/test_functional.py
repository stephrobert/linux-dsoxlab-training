"""Tests pytest+testinfra — l4-bridge-bonding.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le bond en active-backup avec ses deux esclaves, le bridge
avec le bond en port, et la persistance des profils (survie reboot).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_bond_mode_active_backup(host):
    """bond0 doit être en mode active-backup."""
    proc = host.check_output("cat /proc/net/bonding/bond0")
    assert "active-backup" in proc, (
        "bond0 doit être en mode active-backup "
        '(bond.options "mode=active-backup,miimon=100").'
    )


def test_bond_two_slaves(host):
    """bond0 doit avoir dummy1 et dummy2 comme esclaves."""
    proc = host.check_output("cat /proc/net/bonding/bond0")
    assert "dummy1" in proc and "dummy2" in proc, (
        "bond0 doit agréger dummy1 et dummy2 (nmcli con add type dummy ... "
        "master bond0)."
    )


def test_bond_connection_type(host):
    """La connexion bond0 doit être de type bond."""
    ctype = host.check_output("nmcli -g connection.type con show bond0").strip()
    assert ctype == "bond", f"bond0 doit être de type bond (vu : {ctype!r})."


def test_bridge_has_bond_as_port(host):
    """br0 doit être un bridge dont bond0 est un port."""
    ports = host.check_output("ls /sys/class/net/br0/brif/ 2>/dev/null || true")
    assert "bond0" in ports, (
        "bond0 doit être un port du bridge br0 "
        "(nmcli con mod bond0 master br0 slave-type bridge)."
    )


def test_profiles_persist_on_disk(host):
    """Les profils bond0 et br0 doivent être sur disque (persistance reboot)."""
    for name in ("bond0", "br0"):
        profile = host.file(
            f"/etc/NetworkManager/system-connections/{name}.nmconnection"
        )
        assert profile.exists, (
            f"Le profil {name}.nmconnection doit exister (persistance reboot)."
        )
