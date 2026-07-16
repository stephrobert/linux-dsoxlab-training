"""Tests pytest+testinfra — l4-ldap-integration.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : l'utilisateur alice est résolu DEPUIS l'annuaire (pas local),
id fonctionne, et NSS/PAM sont bien basculés sur SSSD (authselect).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_getent_resolves_directory_user(host):
    """getent passwd alice doit résoudre l'utilisateur de l'annuaire (uid 10001)."""
    out = host.check_output("getent passwd alice").strip()
    assert out.startswith("alice:") and ":10001:" in out, (
        f"getent passwd alice doit renvoyer l'utilisateur LDAP uid 10001 "
        f"(vu : {out!r}). Vérifie sssd.conf + authselect + le service sssd."
    )


def test_alice_is_not_local(host):
    """alice ne doit PAS être un compte local (/etc/passwd) — elle vient de LDAP."""
    local = host.check_output("getent -s files passwd alice || true").strip()
    assert local == "", (
        f"alice ne doit pas exister en local (/etc/passwd), elle vient de "
        f"l'annuaire (vu : {local!r})."
    )


def test_id_alice(host):
    """id alice doit fonctionner."""
    out = host.check_output("id alice").strip()
    assert "uid=10001(alice)" in out, (
        f"id alice doit renvoyer uid=10001(alice) (vu : {out!r})."
    )


def test_authselect_profile_is_sssd(host):
    """NSS/PAM doivent être basculés sur SSSD via authselect."""
    out = host.check_output("authselect current").strip()
    assert "sssd" in out, (
        f"Le profil authselect actif doit être sssd (vu : {out!r}). "
        "authselect select sssd with-mkhomedir --force"
    )
