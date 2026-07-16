"""Tests pytest+testinfra — l4-selinux-diagnose-avc.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : contexte restauré, httpd sert le fichier (200 → le refus est
levé), et SELinux toujours enforcing (pas de triche par setenforce 0).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_selinux_enforcing(host):
    """SELinux doit rester enforcing (le désactiver n'est pas la solution)."""
    mode = host.check_output("getenforce").strip()
    assert mode == "Enforcing", f"SELinux doit rester Enforcing (vu : {mode!r})."


def test_context_restored(host):
    """Le fichier doit porter le type httpd_sys_content_t."""
    ctx = host.check_output("ls -Z /var/www/html/index.html")
    assert "httpd_sys_content_t" in ctx, (
        f"/var/www/html/index.html doit être httpd_sys_content_t (vu : {ctx!r}). "
        "restorecon -v /var/www/html/index.html"
    )


def test_httpd_serves_200(host):
    """httpd doit servir le fichier (200) — preuve que le refus est levé."""
    code = host.check_output(
        "curl -s -o /dev/null -w '%{http_code}' http://localhost/index.html"
    ).strip()
    assert code == "200", (
        f"http://localhost/index.html doit renvoyer 200 (vu : {code!r}). "
        "Tant que le contexte est faux, SELinux refuse et httpd renvoie 403."
    )
