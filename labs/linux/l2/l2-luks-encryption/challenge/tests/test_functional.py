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
    """Le disque doit etre formate en LUKS version 2."""
    disk = _disk(host)
    assert disk, "/root/luks-disk.env introuvable (lab non prepare ?)."
    out = host.run(f"cryptsetup luksDump {disk} 2>/dev/null")
    assert out.rc == 0, f"{disk} n'est pas un volume LUKS (cryptsetup luksFormat manquant ?)."
    assert "Version:" in out.stdout and "2" in out.stdout.split("Version:")[1][:8], (
        "Le volume doit etre en LUKS2 (--type luks2)."
    )


def test_mapping_open(host):
    """Le volume doit etre ouvert sous /dev/mapper/coffre."""
    assert host.file("/dev/mapper/coffre").exists, (
        "Ouvrez le volume : cryptsetup open <disque> coffre."
    )


def test_mounted(host):
    """Le volume dechiffre doit etre monte sur /mnt/coffre."""
    out = host.run("findmnt -n /mnt/coffre")
    assert "/dev/mapper/coffre" in out.stdout, (
        "Montez /dev/mapper/coffre sur /mnt/coffre (mkfs.xfs puis mount)."
    )


def test_crypttab_declared(host):
    """L'entree doit figurer dans /etc/crypttab (persistance)."""
    ct = host.file("/etc/crypttab")
    assert ct.exists and "coffre" in ct.content_string, (
        "Declarez le volume dans /etc/crypttab (coffre UUID=... /root/luks.key luks)."
    )
