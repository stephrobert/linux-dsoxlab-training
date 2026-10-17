"""Tests pytest+testinfra — l2-user-lifecycle.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT du compte lu via getent/id : existence, UID, home, shell,
groupe primaire et appartenance au groupe secondaire — pas la commande tapée.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"
USER = "alice"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_user_exists_shell_home(host):
    """alice existe, shell /bin/bash, home /home/alice (répertoire présent)."""
    u = host.user(USER)
    assert u.exists, message(
        en=f"User {USER} must exist (useradd).",
        fr=f"L'utilisateur {USER} doit exister (useradd).",
    )
    assert u.shell == "/bin/bash", message(
        en=f"{USER}'s shell must be /bin/bash (seen: {u.shell}).",
        fr=f"Le shell de {USER} doit être /bin/bash (vu : {u.shell}).",
    )
    assert u.home == "/home/alice", message(
        en=f"{USER}'s home must be /home/alice (seen: {u.home}).",
        fr=f"Le home de {USER} doit être /home/alice (vu : {u.home}).",
    )
    assert host.file("/home/alice").is_directory, message(
        en="The /home/alice directory must exist (useradd -m).",
        fr="Le répertoire /home/alice doit exister (useradd -m).",
    )


def test_uid_is_1500(host):
    """L'UID d'alice doit être 1500."""
    assert host.user(USER).uid == 1500, message(
        en=f"{USER}'s UID must be 1500 (seen: {host.user(USER).uid}). "
        "useradd -u 1500 …",
        fr=f"L'UID de {USER} doit être 1500 (vu : {host.user(USER).uid}). "
        "useradd -u 1500 ...",
    )


def test_primary_group_staff(host):
    """Le groupe PRIMAIRE d'alice doit être staff."""
    assert host.user(USER).group == "staff", message(
        en=f"{USER}'s primary group must be 'staff' "
        f"(seen: {host.user(USER).group}). useradd -g staff …",
        fr=f"Le groupe primaire de {USER} doit être 'staff' "
        f"(vu : {host.user(USER).group}). useradd -g staff ...",
    )


def test_supplementary_group_developers(host):
    """alice doit être membre du groupe SECONDAIRE developers."""
    groups = host.user(USER).groups
    assert "developers" in groups, message(
        en=f"{USER} must belong to the secondary group 'developers' "
        f"(groups seen: {groups}). useradd -G developers … (or usermod -aG).",
        fr=f"{USER} doit appartenir au groupe secondaire 'developers' "
        f"(groupes vus : {groups}). useradd -G developers ... (ou usermod -aG).",
    )
