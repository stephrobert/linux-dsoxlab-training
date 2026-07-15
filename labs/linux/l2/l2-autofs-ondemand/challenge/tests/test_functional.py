"""Tests pytest+testinfra — l2-autofs-ondemand.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : autofs tourne, les cartes existent, et — surtout — accéder à
/autofs/data DÉCLENCHE réellement le montage du bon disque (le témoin est
lisible). C'est le comportement à la demande, pas juste la config.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
KEY = "/autofs/data"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_autofs_running(host):
    """Le service autofs doit tourner."""
    assert host.service("autofs").is_running, (
        "autofs doit être démarré : systemctl enable --now autofs"
    )


def test_master_map(host):
    """La carte maître doit associer /autofs à une carte de montage."""
    found = False
    for path in ("/etc/auto.master", "/etc/auto.master.d/lab.autofs"):
        f = host.file(path)
        if f.exists and "/autofs" in f.content_string:
            found = True
    assert found, (
        "Aucune carte maître ne déclare /autofs. Crée "
        "/etc/auto.master.d/lab.autofs : /autofs  /etc/auto.lab"
    )


def test_mount_map(host):
    """La carte de montage doit décrire la clé 'data' en xfs."""
    f = host.file("/etc/auto.lab")
    assert f.exists, "La carte de montage /etc/auto.lab manque."
    content = f.content_string
    assert "data" in content and "xfs" in content, (
        "La carte /etc/auto.lab doit décrire 'data' en fstype xfs vers le "
        f"disque. Vu :\n{content}"
    )


def test_ondemand_mount_works(host):
    """Accéder à /autofs/data doit monter le disque et servir le témoin."""
    out = host.check_output(
        "cat %s/marker.txt 2>&1; findmnt -no FSTYPE %s 2>/dev/null", KEY, KEY
    )
    assert "autofs" in out, (
        f"Accéder à {KEY} doit monter le disque et rendre marker.txt lisible "
        f"(automontage à la demande). Obtenu :\n{out}"
    )
    assert "xfs" in out, (
        f"{KEY} doit être monté en xfs une fois déclenché (vu :\n{out})."
    )
