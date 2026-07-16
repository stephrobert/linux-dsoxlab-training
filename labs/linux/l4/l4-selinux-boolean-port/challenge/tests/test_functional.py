"""Tests pytest+testinfra — l4-selinux-boolean-port.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT SELinux : booléen ON, port 8404 étiqueté http_port_t, et
SELinux toujours enforcing (pas de triche par setenforce 0).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_selinux_enforcing(host):
    """SELinux doit rester enforcing (désactiver n'est pas la solution)."""
    mode = host.check_output("getenforce").strip()
    assert mode == "Enforcing", (
        f"SELinux doit rester Enforcing (vu : {mode!r})."
    )


def test_boolean_on(host):
    """Le booléen httpd_can_network_connect doit être on."""
    out = host.check_output("getsebool httpd_can_network_connect").strip()
    assert out.endswith("on"), (
        f"httpd_can_network_connect doit être on (vu : {out!r}). "
        "setsebool -P httpd_can_network_connect on"
    )


def test_port_labeled(host):
    """Le port 8404/tcp doit être étiqueté http_port_t."""
    out = host.check_output("semanage port -l")
    http_lines = [
        line for line in out.splitlines()
        if line.startswith("http_port_t") and "tcp" in line
    ]
    assert http_lines and "8404" in " ".join(http_lines), (
        "8404/tcp doit être étiqueté http_port_t "
        "(semanage port -a -t http_port_t -p tcp 8404)."
    )
