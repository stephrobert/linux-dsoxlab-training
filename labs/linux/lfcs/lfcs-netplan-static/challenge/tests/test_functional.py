"""Tests pytest+testinfra — lfcs-netplan-static.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la config netplan sur disque (persistance), l'adresse active
sur lab0 et la route statique — sans toucher l'interface de gestion.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "ubuntu-lfcs-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_netplan_config_declares_static(host):
    """Le fichier netplan doit déclarer l'IP statique (persistance)."""
    cfg = host.file("/etc/netplan/99-lab.yaml")
    assert cfg.exists, "/etc/netplan/99-lab.yaml doit exister."
    assert "192.0.2.50/24" in cfg.content_string, (
        "Le fichier netplan doit déclarer l'adresse 192.0.2.50/24."
    )


def test_static_ip_live(host):
    """lab0 doit porter l'adresse statique en live."""
    out = host.check_output("ip -4 addr show lab0")
    assert "192.0.2.50" in out, (
        "lab0 doit porter 192.0.2.50 en live (netplan apply)."
    )


def test_static_route_present(host):
    """La route statique doit être active."""
    routes = host.check_output("ip route show")
    assert "198.51.100.0/24" in routes, (
        "La route vers 198.51.100.0/24 doit être présente (routes: dans netplan)."
    )
