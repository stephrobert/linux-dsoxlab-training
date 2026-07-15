"""Tests pytest+testinfra — l2-nfs-mount-persist (lab multi-hôte).

Les tests tournent côté CLIENT (alma-rhcsa-1). La fixture autouse
`_apply_lab_state` (conftest.py racine) joue le `solution.yaml` chiffré du
formateur avant les tests (mode CI). En `dsoxlab check`, elle est désactivée
(LAB_NO_REPLAY=1).

On prouve l'ÉTAT : l'export du serveur est monté sur /mnt/nfs, le fichier servi
est lisible (donc le montage fonctionne vraiment), et l'entrée fstab est
persistante avec _netdev.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

CLIENT_HOST = "alma-rhcsa-1.lab"
MOUNT = "/mnt/nfs"


@pytest.fixture(scope="module")
def host():
    return lab_host(CLIENT_HOST)


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
    """/mnt/nfs doit être monté (l'export NFS du serveur)."""
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} n'est pas monté. Après l'entrée fstab : sudo mount -a"
    )


def test_type_is_nfs(host):
    """Le montage doit être de type NFS."""
    fstype = host.check_output("findmnt -no FSTYPE %s", MOUNT)
    assert fstype.startswith("nfs"), (
        f"{MOUNT} doit être un montage NFS (vu : {fstype!r})."
    )


def test_served_file_readable(host):
    """Le fichier servi par le serveur doit être lisible via le montage."""
    f = host.file(f"{MOUNT}/hello.txt")
    assert f.exists, (
        f"{MOUNT}/hello.txt introuvable : le montage NFS ne sert pas le contenu "
        "du serveur (mauvais export, ou montage échoué)."
    )


def test_fstab_persistent_netdev(host):
    """L'entrée fstab doit être persistante avec _netdev (montage réseau)."""
    line = _fstab_line(host)
    assert line is not None, (
        f"Aucune entrée fstab pour {MOUNT}. Ajoute : "
        "<serveur>:/srv/export /mnt/nfs nfs _netdev,defaults 0 0"
    )
    fields = line.split()
    assert len(fields) >= 4 and fields[2].startswith("nfs"), (
        f"L'entrée fstab de {MOUNT} doit être de type nfs (vu : {line!r})."
    )
    assert "_netdev" in fields[3].split(","), (
        "L'option _netdev est requise pour un montage réseau (attend le réseau "
        f"au boot). Vu : {fields[3]!r}."
    )
