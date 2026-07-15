"""Tests pytest+testinfra — l3-fs-readonly-recover.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : /srv/data remonté en lecture-écriture, réellement inscriptible,
et un fstab propre (mount -a réussit — plus d'option invalide).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
MOUNT = "/srv/data"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_mounted_read_write(host):
    """/srv/data doit être monté en lecture-écriture (plus en ro)."""
    opts = host.check_output("findmnt -no OPTIONS %s", MOUNT).split(",")
    assert "rw" in opts, (
        f"{MOUNT} doit être remonté en lecture-écriture (vu : {opts}). "
        f"mount -o remount,rw {MOUNT}"
    )
    assert "ro" not in opts, f"{MOUNT} est encore en lecture seule (options : {opts})."


def test_writable(host):
    """/srv/data doit être réellement inscriptible."""
    rc = host.run("touch /srv/data/.rw_probe && rm -f /srv/data/.rw_probe").rc
    assert rc == 0, (
        f"{MOUNT} doit être inscriptible : l'écriture d'un fichier de test a échoué."
    )


def test_fstab_clean(host):
    """mount -a doit réussir : l'option invalide de fstab a été corrigée."""
    result = host.run("mount -a")
    assert result.rc == 0, (
        "mount -a échoue encore : l'entrée fstab de /srv/data a toujours une "
        f"option invalide (corrige « defalts » en « defaults »).\n{result.stderr}"
    )


def test_no_bad_option_in_fstab(host):
    """L'option fautive ne doit plus figurer dans /etc/fstab."""
    fstab = host.file("/etc/fstab").content_string
    assert "defalts" not in fstab, (
        "L'option invalide « defalts » est encore dans /etc/fstab — remplace-la "
        "par « defaults »."
    )
