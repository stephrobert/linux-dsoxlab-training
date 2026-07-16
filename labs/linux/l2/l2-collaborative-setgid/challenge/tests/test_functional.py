"""Tests pytest+testinfra — l2-collaborative-setgid.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le répertoire (groupe + bit set-GID + écriture groupe) ET
l'effet réel — un fichier créé par un membre hérite du groupe devteam.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_directory_group_and_setgid(host):
    """/srv/partage : répertoire, groupe devteam, mode set-GID + g+w."""
    d = host.file("/srv/partage")
    assert d.is_directory, "/srv/partage doit être un répertoire."
    assert d.group == "devteam", (
        f"/srv/partage doit avoir le groupe devteam (vu : {d.group}). "
        "chgrp devteam /srv/partage"
    )
    assert d.mode & 0o2000, (
        f"Le bit set-GID doit être posé (mode vu : {oct(d.mode)}). chmod 2775"
    )
    assert d.mode & 0o0020, (
        "Le groupe doit avoir le droit d'écriture (g+w) — mode 2775."
    )


def test_new_file_inherits_group(host):
    """Un fichier créé par un membre doit hériter du groupe devteam (set-GID)."""
    host.run("rm -f /srv/partage/probe")
    res = host.run("runuser -u alice -- touch /srv/partage/probe")
    assert res.rc == 0, f"Création du témoin échouée : {res.stderr}"
    probe = host.file("/srv/partage/probe")
    assert probe.group == "devteam", (
        f"Un fichier créé dans /srv/partage doit hériter du groupe devteam "
        f"(vu : {probe.group}) — c'est l'effet du bit set-GID."
    )
