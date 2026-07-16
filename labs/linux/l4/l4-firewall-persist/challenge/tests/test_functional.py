"""Tests pytest+testinfra — l4-firewall-persist.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : http ouvert en runtime ET en permanent (persistance reboot),
et ssh toujours autorisé (pas de régression d'accès).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_http_runtime(host):
    """http doit être ouvert dans la zone active (runtime)."""
    services = host.check_output("firewall-cmd --list-services").split()
    assert "http" in services, (
        f"http doit être dans les services runtime (vu : {services}). "
        "firewall-cmd --permanent --add-service=http && firewall-cmd --reload"
    )


def test_http_permanent(host):
    """http doit être permanent (sinon perdu au reboot)."""
    services = host.check_output(
        "firewall-cmd --permanent --list-services"
    ).split()
    assert "http" in services, (
        f"http doit être permanent (vu : {services}). "
        "firewall-cmd --permanent --add-service=http"
    )


def test_ssh_still_allowed(host):
    """ssh ne doit jamais être fermé (accès de gestion)."""
    services = host.check_output("firewall-cmd --list-services").split()
    assert "ssh" in services, (
        f"ssh doit rester autorisé (vu : {services}) — ne le ferme jamais."
    )
