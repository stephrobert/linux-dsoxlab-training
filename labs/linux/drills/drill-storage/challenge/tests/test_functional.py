"""Tests fonctionnels — drill-storage.

5 tests = 5 tâches. On interroge les outils eux-mêmes (lsblk, pvs/vgs/lvs,
findmnt, swapon) plutôt que des fichiers : ce qui compte est l'état RÉEL du
stockage, pas ce qui est écrit quelque part.

Drill BI-DISTRIB : hôte non codé en dur (`lab_target_host()`, dsoxlab >= 0.1.7).
parted, LVM, XFS et mkswap se comportent à l'identique sur RHEL et Debian.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")
MOUNT = "/mnt/data"
GIB = 1024 ** 3


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _fstab_line(host, mount: str) -> str | None:
    for ligne in host.file("/etc/fstab").content_string.splitlines():
        nette = ligne.strip()
        if nette.startswith("#"):
            continue
        champs = nette.split()
        if len(champs) >= 2 and champs[1] == mount:
            return nette
    return None


@pytest.mark.points(20)
def test_task1_gpt_partitions(host):
    """/dev/vdb doit porter une table GPT et deux partitions (2 Gio / 1 Gio)."""
    label = host.check_output(
        "lsblk -dno PTTYPE /dev/vdb 2>/dev/null || true"
    ).strip()
    assert label == "gpt", (
        f"/dev/vdb doit porter une table de partitions GPT (vu : {label!r})."
    )
    for part, attendu_gio in (("/dev/vdb1", 2), ("/dev/vdb2", 1)):
        taille = host.check_output("lsblk -bdno SIZE %s", part)
        gio = int(taille) / GIB
        assert abs(gio - attendu_gio) < 0.15, (
            f"{part} doit faire environ {attendu_gio} Gio (vu : {gio:.2f} Gio)."
        )


@pytest.mark.points(20)
def test_task2_lvm_stack(host):
    """vgdrill doit reposer sur /dev/vdb1, et porter lvdata en XFS."""
    pvs = host.check_output("pvs --noheadings -o pv_name,vg_name")
    assert "/dev/vdb1" in pvs and "vgdrill" in pvs, (
        f"/dev/vdb1 doit être un PV du groupe vgdrill. Vu :\n{pvs}"
    )
    lvs = host.check_output("lvs --noheadings -o lv_name,vg_name")
    assert "lvdata" in lvs and "vgdrill" in lvs, (
        f"Le volume logique lvdata doit exister dans vgdrill. Vu :\n{lvs}"
    )
    fstype = host.check_output(
        "blkid -s TYPE -o value /dev/vgdrill/lvdata 2>/dev/null || true"
    ).strip()
    assert fstype == "xfs", (
        f"lvdata doit être formaté en XFS (vu : {fstype!r})."
    )


@pytest.mark.points(20)
def test_task3_mounted_by_uuid(host):
    """/mnt/data monté depuis lvdata, persistant PAR UUID."""
    assert host.mount_point(MOUNT).exists, f"{MOUNT} n'est pas monté."
    source = host.check_output("findmnt -no SOURCE %s", MOUNT)
    assert "vgdrill" in source and "lvdata" in source, (
        f"{MOUNT} doit être monté depuis vgdrill/lvdata (vu : {source})."
    )
    ligne = _fstab_line(host, MOUNT)
    assert ligne is not None, (
        f"Aucune entrée fstab pour {MOUNT} : le montage serait perdu au reboot."
    )
    assert ligne.split()[0].startswith("UUID="), (
        "L'entrée fstab doit référencer le système de fichiers par UUID=, pas "
        f"par chemin de device. Vu : {ligne!r}"
    )


@pytest.mark.points(20)
def test_task4_swapfile(host):
    """/swapfile de 128 Mio, actif et persistant."""
    swaps = host.check_output("swapon --show=NAME --noheadings || true")
    assert "/swapfile" in swaps, (
        f"/swapfile n'est pas un swap actif. Vu : {swaps!r}"
    )
    taille = int(host.check_output("stat -c %%s %s", "/swapfile"))
    mio = taille // (1024 * 1024)
    assert 125 <= mio <= 131, f"/swapfile doit faire ~128 Mio (vu : {mio} Mio)."
    ligne = next(
        (entree for entree in host.file("/etc/fstab").content_string.splitlines()
         if "/swapfile" in entree and not entree.strip().startswith("#")),
        None,
    )
    assert ligne is not None and "swap" in ligne.split(), (
        "Aucune entrée fstab de type swap pour /swapfile : le swap serait "
        "perdu au reboot."
    )


@pytest.mark.points(20)
def test_task5_extended_online(host):
    """lvdata étendu à 1.5 Gio, et le FS XFS suit — sans démontage."""
    taille_lv = host.check_output(
        "lvs --noheadings --units b --nosuffix -o lv_size /dev/vgdrill/lvdata"
    ).strip()
    gio_lv = int(float(taille_lv)) / GIB
    assert gio_lv >= 1.45, (
        f"lvdata doit être étendu à 1,5 Gio (vu : {gio_lv:.2f} Gio)."
    )
    # Étendre le LV ne suffit pas : le système de fichiers doit avoir suivi.
    # C'est LE piège — sans xfs_growfs, l'espace n'est pas utilisable.
    taille_fs = host.check_output("findmnt -bno SIZE %s", MOUNT)
    gio_fs = int(taille_fs) / GIB
    assert gio_fs >= 1.4, (
        "Le volume logique a été étendu mais PAS le système de fichiers : "
        f"l'espace n'est pas utilisable. Le FS ne fait que {gio_fs:.2f} Gio "
        f"pour un LV de {gio_lv:.2f} Gio. Il fallait faire suivre XFS."
    )
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} doit toujours être monté : l'extension se fait à chaud."
    )
