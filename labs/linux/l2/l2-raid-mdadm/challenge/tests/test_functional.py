"""Tests pytest+testinfra — l2-raid-mdadm."""
from __future__ import annotations

import re

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_array_is_raid1_active(host):
    """/dev/md0 doit etre un RAID 1 actif avec 2 disques."""
    out = host.run("mdadm --detail /dev/md0 2>/dev/null")
    assert out.rc == 0, "/dev/md0 introuvable : creez le RAID avec mdadm --create."
    assert "raid1" in out.stdout, "Le niveau doit etre raid1."
    assert "Active Devices : 2" in out.stdout, "Le RAID doit compter 2 disques actifs."
    assert "State : clean" in out.stdout or "active" in out.stdout, "L'array doit etre sain (clean/active)."


def test_array_mounted(host):
    """Le RAID doit etre monte sur /mnt/raid."""
    out = host.run("findmnt -n /mnt/raid")
    assert "/dev/md0" in out.stdout, "Montez /dev/md0 sur /mnt/raid (mkfs.xfs puis mount)."


def test_array_persistent(host):
    """L'array doit etre declare dans /etc/mdadm.conf (persistance)."""
    conf = host.file("/etc/mdadm.conf")
    # mdadm --detail --scan ecrit "/dev/md0" ou "/dev/md/0" selon la facon dont
    # la grappe a ete nommee, et "/dev/md127" si elle a ete reassemblee sans
    # mdadm.conf. On accepte les trois : ce qui compte est qu'une ligne ARRAY
    # declare la grappe, pas la forme exacte de son nom.
    assert conf.exists, (
        "Ajoutez l'array a /etc/mdadm.conf : mdadm --detail --scan >> /etc/mdadm.conf"
    )
    assert re.search(r"^ARRAY\s+/dev/md/?\d+", conf.content_string, re.M), (
        "Aucune ligne ARRAY dans /etc/mdadm.conf. "
        "Ajoutez-la : mdadm --detail --scan >> /etc/mdadm.conf"
    )
