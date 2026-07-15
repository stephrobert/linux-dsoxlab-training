"""Tests pytest+testinfra — l2-storage-performance.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : /srv/data monté AVEC noatime actif (options du montage réel),
ET noatime déclaré dans /etc/fstab (persistance reboot).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
MOUNT = "/srv/data"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _fstab_line(host) -> str | None:
    fstab = host.file("/etc/fstab").content_string
    for line in fstab.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2 and fields[1] == MOUNT:
            return stripped
    return None


def test_mounted(host):
    """/srv/data doit rester monté."""
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} n'est pas monté. Après avoir édité fstab : mount -o remount {MOUNT}"
    )


def test_noatime_active(host):
    """Le montage réel de /srv/data doit inclure l'option noatime."""
    opts = host.check_output("findmnt -no OPTIONS %s", MOUNT)
    assert "noatime" in opts.split(","), (
        f"noatime n'est pas actif sur {MOUNT} (options : {opts}). "
        f"Ajoute-le puis : mount -o remount {MOUNT}"
    )


def test_noatime_persistent_in_fstab(host):
    """L'option noatime doit figurer dans /etc/fstab (persistance après reboot)."""
    line = _fstab_line(host)
    assert line is not None, (
        f"Aucune entrée fstab non commentée pour {MOUNT}."
    )
    options = line.split()[3] if len(line.split()) >= 4 else ""
    assert "noatime" in options.split(","), (
        f"L'entrée fstab de {MOUNT} doit inclure noatime dans ses options "
        f"(vu : {options!r}), sinon le réglage ne survit pas au reboot."
    )
