"""Tests pytest+testinfra — l2-luks-encryption."""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _disk(host) -> str:
    out = host.run("grep '^DISK=' /root/luks-disk.env | cut -d= -f2")
    return out.stdout.strip()


def test_disk_is_luks2(host):
    """Le disque doit être formaté en LUKS version 2."""
    disk = _disk(host)
    assert disk, "/root/luks-disk.env introuvable (lab non préparé ?)."
    out = host.run(f"cryptsetup luksDump {disk} 2>/dev/null")
    assert out.rc == 0, f"{disk} n'est pas un volume LUKS (cryptsetup luksFormat manquant ?)."
    assert "Version:" in out.stdout, (
        f"{disk} ne présente pas d'en-tête LUKS lisible."
    )
    # On lit la VALEUR du champ, pas une fenêtre de caractères : cryptsetup
    # aligne la colonne avec des espaces puis une tabulation, si bien que le
    # chiffre tombait en 9e position et échappait à une tranche [:8]. Le
    # volume était bien en LUKS2, seul le test se trompait.
    version = out.stdout.split("Version:", 1)[1].splitlines()[0].strip()
    assert version == "2", (
        f"Le volume doit être en LUKS2 (--type luks2), version lue : {version!r}."
    )


def test_mapping_open(host):
    """Le volume doit être ouvert sous /dev/mapper/coffre."""
    assert host.file("/dev/mapper/coffre").exists, (
        "Ouvrez le volume : cryptsetup open <disque> coffre."
    )


def test_mounted(host):
    """Le volume déchiffré doit être monté sur /mnt/coffre."""
    out = host.run("findmnt -n /mnt/coffre")
    assert "/dev/mapper/coffre" in out.stdout, (
        "Montez /dev/mapper/coffre sur /mnt/coffre (mkfs.xfs puis mount)."
    )


def test_crypttab_declared(host):
    """L'entrée doit figurer dans /etc/crypttab (persistance)."""
    ct = host.file("/etc/crypttab")
    assert ct.exists, (
        "/etc/crypttab n'existe pas : le volume ne serait pas rouvert au "
        "démarrage."
    )
    # On lit le NOM DE MAPPING, premier champ d'une ligne active, plutôt que
    # de chercher « coffre » dans tout le fichier : un commentaire laissé par
    # une session précédente suffirait sinon à valider une persistance absente.
    noms = {
        ligne.split()[0]
        for ligne in ct.content_string.splitlines()
        if ligne.strip() and not ligne.strip().startswith("#")
    }
    assert "coffre" in noms, (
        "Déclarez le volume dans /etc/crypttab "
        "(coffre UUID=... /root/luks.key luks). Mappings déclarés : "
        f"{sorted(noms) or 'aucun'}."
    )
