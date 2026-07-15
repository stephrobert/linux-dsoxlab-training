"""Tests pytest+testinfra — l2-filesystem-create-xfs.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` du formateur (chiffré ansible-vault) avant les tests en mode CI.
En `dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la partition porte réellement un XFS, avec le bon label, et
elle est montée — lu via blkid/testinfra, pas la commande tapée.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
MOUNT = "/srv/xfs"
LABEL = "DATA"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module")
def part(host) -> str:
    """Partition cible, lue depuis l'env posé par le setup."""
    out = host.check_output("cat /root/xfs-disk.env")
    for line in out.splitlines():
        if line.startswith("PART="):
            return line.split("=", 1)[1].strip()
    pytest.fail("/root/xfs-disk.env sans PART= (setup non joué ?)")


def test_filesystem_is_xfs(host, part):
    """La partition doit porter un filesystem XFS."""
    fstype = host.check_output("blkid -s TYPE -o value %s || true", part)
    assert fstype == "xfs", (
        f"{part} doit être formaté en XFS (vu : {fstype!r}). "
        f"Utilise : mkfs.xfs -L {LABEL} {part}"
    )


def test_filesystem_label(host, part):
    """Le filesystem doit porter le label DATA."""
    label = host.check_output("blkid -s LABEL -o value %s || true", part)
    assert label == LABEL, (
        f"Le filesystem doit avoir le label {LABEL!r} (vu : {label!r}). "
        f"mkfs.xfs -L {LABEL} ... ou xfs_admin -L {LABEL} {part}"
    )


def test_mounted_at_target(host):
    """Le filesystem doit être monté sur /srv/xfs."""
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} n'est pas monté. Crée le point de montage puis : mount ... {MOUNT}"
    )


def test_mount_type_is_xfs(host):
    """Le montage sur /srv/xfs doit être de type xfs."""
    mp = host.mount_point(MOUNT)
    assert mp.exists and mp.filesystem == "xfs", (
        f"{MOUNT} doit être un montage XFS (vu : {mp.filesystem if mp.exists else 'non monté'})."
    )
