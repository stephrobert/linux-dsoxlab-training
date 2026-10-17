"""Tests pytest+testinfra — l4-ssh-key-auth-harden.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : l'utilisateur deploy, et surtout les permissions/propriétaire
exacts qui font que sshd accepte (ou non) la clé.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"
KEY_FINGERPRINT = "AAAAC3NzaC1lZDI1NTE5AAAAIKLo0f6RPaHxkK8hieq9X35N92QlJIUqBNU1UsQc+ntg"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.mark.garde_fou
def test_deploy_user_exists(host):
    """L'utilisateur deploy doit exister."""
    assert host.user("deploy").exists, message(
        en="User deploy must exist.",
        fr="L'utilisateur deploy doit exister.",
    )


def test_ssh_dir_perms(host):
    """~deploy/.ssh doit être 0700 deploy:deploy."""
    d = host.file("/home/deploy/.ssh")
    assert d.is_directory, message(
        en="~deploy/.ssh must be a directory.",
        fr="~deploy/.ssh doit être un répertoire.",
    )
    assert d.mode == 0o700, message(
        en=f"~deploy/.ssh must be 0700 (seen: {oct(d.mode)}).",
        fr=f"~deploy/.ssh doit être 0700 (vu : {oct(d.mode)}).",
    )
    assert d.user == "deploy" and d.group == "deploy", message(
        en=f"~deploy/.ssh must belong to deploy:deploy (seen: {d.user}:{d.group}).",
        fr=f"~deploy/.ssh doit appartenir à deploy:deploy (vu : {d.user}:{d.group}).",
    )


def test_authorized_keys(host):
    """authorized_keys doit être 0600 deploy:deploy et contenir la clé."""
    f = host.file("/home/deploy/.ssh/authorized_keys")
    assert f.exists, message(
        en="authorized_keys must exist.",
        fr="authorized_keys doit exister.",
    )
    assert f.mode == 0o600, message(
        en=f"authorized_keys must be 0600 (seen: {oct(f.mode)}).",
        fr=f"authorized_keys doit être 0600 (vu : {oct(f.mode)}).",
    )
    assert f.user == "deploy" and f.group == "deploy", message(
        en=f"authorized_keys must belong to deploy:deploy (seen: {f.user}:{f.group}).",
        fr=f"authorized_keys doit appartenir à deploy:deploy (vu : {f.user}:{f.group}).",
    )
    assert KEY_FINGERPRINT in f.content_string, message(
        en="The lab's public key must stay present in authorized_keys.",
        fr="La clé publique du lab doit rester présente dans authorized_keys.",
    )
