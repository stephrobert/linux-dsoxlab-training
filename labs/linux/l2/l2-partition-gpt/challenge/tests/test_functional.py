"""Tests pytest+testinfra — l2-partition-gpt.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` du formateur sur la VM avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1) pour tester le
travail manuel de l'apprenant.

On prouve l'ÉTAT du disque : table GPT réelle, deux partitions, et leurs
tailles — lues via lsblk/blkid, pas la commande tapée.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
MIB = 1024 * 1024


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module")
def disk(host) -> str:
    """Chemin du disque additionnel, lu depuis l'env posé par le setup."""
    out = host.check_output("cat /root/part-disk.env")
    for line in out.splitlines():
        if line.startswith("DISK="):
            return line.split("=", 1)[1].strip()
    pytest.fail("/root/part-disk.env introuvable ou sans DISK= (setup non joué ?)")


def _partitions(host, disk: str) -> list[str]:
    base = disk.rsplit("/", 1)[-1]
    names = host.check_output("lsblk -lno NAME %s", disk).split()
    return [n for n in names if n != base]


def test_gpt_label(host, disk):
    """Le disque doit porter une table de partition GPT."""
    pttype = host.check_output("blkid -s PTTYPE -o value %s || true", disk)
    assert pttype == "gpt", (
        f"{disk} doit avoir une table GPT (vu : {pttype!r}). "
        f"Utilise : parted -s {disk} mklabel gpt"
    )


def test_two_partitions(host, disk):
    """Le disque doit avoir au moins deux partitions."""
    parts = _partitions(host, disk)
    assert len(parts) >= 2, (
        f"Le disque doit avoir 2 partitions, trouvé {len(parts)} : {parts}. "
        "Crée-les avec parted mkpart, puis partprobe."
    )


def test_partition1_is_512mib(host, disk):
    """La 1re partition doit faire ~512 Mio."""
    parts = _partitions(host, disk)
    assert parts, "Aucune partition trouvée."
    size = int(host.check_output("lsblk -bno SIZE /dev/%s", parts[0]))
    assert 509 * MIB <= size <= 515 * MIB, (
        f"La 1re partition doit faire ~512 Mio (vue : {size // MIB} Mio). "
        f"parted -s {disk} mkpart primary 1MiB 513MiB"
    )


def test_partition2_is_1gib(host, disk):
    """La 2e partition doit faire ~1 Gio."""
    parts = _partitions(host, disk)
    assert len(parts) >= 2, "Deuxième partition absente."
    size = int(host.check_output("lsblk -bno SIZE /dev/%s", parts[1]))
    assert 1021 * MIB <= size <= 1027 * MIB, (
        f"La 2e partition doit faire ~1 Gio (vue : {size // MIB} Mio). "
        f"parted -s {disk} mkpart primary 513MiB 1537MiB"
    )
