"""Tests pytest+testinfra — l4-reverse-proxy-lb.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : HAProxy actif+enabled (persistance), et surtout une VRAIE
requête à travers le proxy renvoie la page du backend.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_haproxy_running_and_enabled(host):
    """haproxy doit tourner ET être enabled (persistance reboot)."""
    svc = host.service("haproxy")
    assert svc.is_running, "haproxy doit tourner : systemctl start haproxy"
    assert svc.is_enabled, (
        "haproxy doit être enabled (sinon perdu au reboot) : "
        "systemctl enable haproxy"
    )


def test_config_has_frontend_and_backend(host):
    """La conf doit déclarer un frontend et un backend avec un server."""
    cfg = host.file("/etc/haproxy/haproxy.cfg").content_string
    assert "frontend" in cfg and "backend" in cfg and "server" in cfg, (
        "haproxy.cfg doit contenir un frontend, un backend et une ligne server."
    )


def test_request_through_proxy(host):
    """Une requête à travers le proxy doit renvoyer la page du backend."""
    body = host.check_output("curl -s http://localhost/")
    assert "backend-ok" in body, (
        f"curl http://localhost/ doit renvoyer 'backend-ok' via le proxy "
        f"(vu : {body!r}). Le frontend doit router vers le backend."
    )
