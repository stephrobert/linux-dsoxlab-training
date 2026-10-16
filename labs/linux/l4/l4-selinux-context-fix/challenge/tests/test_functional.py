"""Tests pytest+testinfra — l4-selinux-context-fix.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT SELinux : le type actif du fichier ET la règle fcontext
persistante (survit à un relabel), SELinux toujours enforcing.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.mark.garde_fou
def test_selinux_enforcing(host):
    """SELinux doit rester enforcing."""
    mode = host.check_output("getenforce").strip()
    assert mode == "Enforcing", message(
        en=f"SELinux must stay Enforcing (seen: {mode!r}). Disabling it would "
        "make the test pass without the context ever being fixed.",
        fr=f"SELinux doit rester Enforcing (vu : {mode!r}). Le désactiver ferait "
        "passer le test sans que le contexte ait été corrigé.",
    )


def test_live_context(host):
    """Le fichier doit porter le type httpd_sys_content_t (actif)."""
    ctx = host.check_output("ls -Z /srv/labweb/index.html")
    assert "httpd_sys_content_t" in ctx, message(
        en=f"/srv/labweb/index.html must be httpd_sys_content_t (seen: {ctx!r}). "
        "restorecon -Rv /srv/labweb after the fcontext rule",
        fr=f"/srv/labweb/index.html doit être httpd_sys_content_t (vu : {ctx!r}). "
        "restorecon -Rv /srv/labweb après la règle fcontext",
    )


def test_fcontext_rule_persistent(host):
    """Une règle fcontext persistante doit exister (survit au relabel)."""
    out = host.check_output("semanage fcontext -l")
    rule_lines = [line for line in out.splitlines() if "/srv/labweb" in line]
    assert rule_lines and "httpd_sys_content_t" in rule_lines[0], message(
        en="A semanage fcontext rule /srv/labweb → httpd_sys_content_t must "
        "exist (otherwise lost at relabel). chcon alone is not enough.",
        fr="Une règle semanage fcontext /srv/labweb → httpd_sys_content_t doit "
        "exister (sinon perdu au relabel). chcon seul ne suffit pas.",
    )
