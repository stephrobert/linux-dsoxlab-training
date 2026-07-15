"""Tests pytest+testinfra — l2-lvm-extend-persist.

Prouve l'ÉTAT du système, pas les commandes tapées : le LV est réellement
étendu, le XFS reflète l'extension (le piège n°1 : étendre le LV sans agrandir
le filesystem), et le montage est persistant via /etc/fstab par UUID.

En CI, la fixture autouse du conftest racine rejoue la solution du formateur
avant les tests. En `dsoxlab check` (LAB_NO_REPLAY=1), les tests valident le
travail de l'apprenant.
"""
from __future__ import annotations

import re

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_data_mounted_xfs(host):
    """/data doit être un point de montage XFS."""
    mp = host.mount_point("/data")
    assert mp.exists, "/data n'est pas un point de montage."
    assert mp.filesystem == "xfs", f"FS attendu xfs, trouvé {mp.filesystem}."


def test_lv_extended_to_3g(host):
    """Le LV vgdata/lvdata doit faire au moins 3 GiB (lvextend)."""
    out = host.run("lvs --noheadings --units g -o lv_size vgdata/lvdata")
    assert out.rc == 0, "LV vgdata/lvdata introuvable."
    size = float(out.stdout.strip().rstrip("gG").replace(",", "."))
    assert size >= 2.95, (
        f"lvdata doit faire au moins 3 GiB (vu {size} GiB). "
        "Étends-le : lvextend -L 3G /dev/vgdata/lvdata"
    )


def test_xfs_reflects_extension(host):
    """Le piège n°1 : le XFS de /data doit refléter l'extension du LV.

    Étendre le LV sans agrandir le filesystem laisse l'espace invisible.
    """
    df = host.run("df -BG --output=size /data | tail -1")
    df_size = int(df.stdout.strip().rstrip("G").strip())
    assert df_size >= 3, (
        f"Le XFS sur /data ne reflète pas l'extension (vu {df_size}G). "
        "Après lvextend : xfs_growfs /data"
    )


def test_mount_persistent_fstab_uuid(host):
    """Le montage /data doit être déclaré dans /etc/fstab par UUID (persistance)."""
    fstab = host.file("/etc/fstab").content_string
    assert re.search(r"^\s*UUID=\S+\s+/data\s+xfs", fstab, re.MULTILINE), (
        "Le montage /data doit figurer dans /etc/fstab par UUID en xfs "
        "(sinon il ne survit pas au reboot)."
    )
