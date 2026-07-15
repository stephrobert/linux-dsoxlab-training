"""Tests pytest+testinfra — l2-fstab-persist-uuid.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` du formateur sur la VM avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1) pour tester le
travail manuel de l'apprenant.

On prouve l'ÉTAT réel : montage actif, type ext4, et surtout entrée fstab
par UUID (pas par nom de périphérique) dont l'UUID correspond au disque —
c'est ce qui garantit la persistance après reboot.
"""
from __future__ import annotations

import re

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
MOUNT = "/srv/data"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _fstab_line(host) -> str | None:
    """Retourne la ligne fstab non commentée qui monte /srv/data, sinon None."""
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
    """/srv/data doit être un point de montage actif."""
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} n'est pas monté. Après avoir écrit l'entrée fstab : sudo mount -a"
    )


def test_filesystem_is_ext4(host):
    """Le filesystem monté sur /srv/data doit être ext4."""
    assert host.mount_point(MOUNT).filesystem == "ext4", (
        f"{MOUNT} doit être un ext4 (vu : {host.mount_point(MOUNT).filesystem})."
    )


def test_fstab_entry_by_uuid(host):
    """L'entrée fstab de /srv/data doit référencer le disque par UUID, pas /dev/."""
    line = _fstab_line(host)
    assert line is not None, (
        f"Aucune entrée fstab non commentée pour {MOUNT}. Ajoutez : "
        f"UUID=<uuid> {MOUNT} ext4 defaults 0 0"
    )
    device = line.split()[0]
    assert device.upper().startswith("UUID="), (
        f"L'entrée fstab doit référencer le disque par UUID (piège RHCSA : un "
        f"nom /dev/vdX peut changer au reboot). Vu : {device!r}. "
        "Récupérez l'UUID avec blkid."
    )


def test_fstab_uuid_matches_device(host):
    """L'UUID écrit dans fstab doit être celui du disque réellement monté."""
    line = _fstab_line(host)
    assert line is not None, "Entrée fstab pour /srv/data absente."
    m = re.match(r'UUID=("?)([^"\s]+)\1', line, re.IGNORECASE)
    assert m, f"UUID illisible dans l'entrée fstab : {line!r}"
    fstab_uuid = m.group(2)

    source = host.check_output("findmnt -no SOURCE %s", MOUNT)
    real_uuid = host.check_output("blkid -s UUID -o value %s", source)
    assert fstab_uuid == real_uuid, (
        f"L'UUID de fstab ({fstab_uuid}) ne correspond pas au disque monté "
        f"({real_uuid}). L'entrée doit pointer le bon filesystem."
    )
