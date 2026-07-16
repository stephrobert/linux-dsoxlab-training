"""Tests pytest+testinfra — lfcs-firewall-ufw.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : ufw actif, http ouvert, et SSH toujours autorisé (pas de
régression d'accès).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "ubuntu-lfcs-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_ufw_active(host):
    """ufw doit être actif."""
    status = host.check_output("ufw status")
    assert status.splitlines()[0].strip() == "Status: active", (
        f"ufw doit être actif (vu : {status.splitlines()[0]!r}). sudo ufw enable"
    )


def test_http_allowed(host):
    """Le service http (80/tcp) doit être autorisé."""
    status = host.check_output("ufw status")
    assert "80/tcp" in status or "http" in status.lower(), (
        "http (80/tcp) doit être autorisé : sudo ufw allow http"
    )


def test_ssh_still_allowed(host):
    """OpenSSH doit rester autorisé (accès de gestion)."""
    status = host.check_output("ufw status")
    assert "OpenSSH" in status or "22/tcp" in status, (
        "OpenSSH doit rester autorisé — ne le retire jamais."
    )
