"""Tests pytest+testinfra — l4-ssh-key-auth-harden.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : l'utilisateur deploy, et surtout les permissions/propriétaire
exacts qui font que sshd accepte (ou non) la clé.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
KEY_FINGERPRINT = "AAAAC3NzaC1lZDI1NTE5AAAAIKLo0f6RPaHxkK8hieq9X35N92QlJIUqBNU1UsQc+ntg"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_deploy_user_exists(host):
    """L'utilisateur deploy doit exister."""
    assert host.user("deploy").exists, "L'utilisateur deploy doit exister."


def test_ssh_dir_perms(host):
    """~deploy/.ssh doit être 0700 deploy:deploy."""
    d = host.file("/home/deploy/.ssh")
    assert d.is_directory, "~deploy/.ssh doit être un répertoire."
    assert d.mode == 0o700, f"~deploy/.ssh doit être 0700 (vu : {oct(d.mode)})."
    assert d.user == "deploy" and d.group == "deploy", (
        f"~deploy/.ssh doit appartenir à deploy:deploy (vu : {d.user}:{d.group})."
    )


def test_authorized_keys(host):
    """authorized_keys doit être 0600 deploy:deploy et contenir la clé."""
    f = host.file("/home/deploy/.ssh/authorized_keys")
    assert f.exists, "authorized_keys doit exister."
    assert f.mode == 0o600, (
        f"authorized_keys doit être 0600 (vu : {oct(f.mode)})."
    )
    assert f.user == "deploy" and f.group == "deploy", (
        f"authorized_keys doit appartenir à deploy:deploy (vu : {f.user}:{f.group})."
    )
    assert KEY_FINGERPRINT in f.content_string, (
        "La clé publique du lab doit rester présente dans authorized_keys."
    )
