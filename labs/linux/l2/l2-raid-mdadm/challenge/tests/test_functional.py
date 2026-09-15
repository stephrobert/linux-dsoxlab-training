"""Tests pytest+testinfra — l2-raid-mdadm."""
from __future__ import annotations

import re

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _champs(sortie: str) -> dict[str, str]:
    """Rend les lignes « clé : valeur » de `mdadm --detail` en dictionnaire.

    Lire des champs plutôt que des sous-chaînes n'est pas une coquetterie :
    « Active Devices : 2 » se trouve aussi dans « Active Devices : 20 », et le
    mot « active » se trouve dans « Active Devices » quel que soit l'état réel
    de la grappe.
    """
    champs = {}
    for ligne in sortie.splitlines():
        if ":" in ligne:
            cle, valeur = ligne.split(":", 1)
            champs[cle.strip()] = valeur.strip()
    return champs


def test_array_is_raid1_active(host):
    """/dev/md0 doit être un RAID 1 actif avec 2 disques."""
    out = host.run("mdadm --detail /dev/md0 2>/dev/null")
    assert out.rc == 0, "/dev/md0 introuvable : créez le RAID avec mdadm --create."

    champs = _champs(out.stdout)
    assert champs.get("Raid Level") == "raid1", (
        f"Le niveau doit être raid1, lu : {champs.get('Raid Level')!r}."
    )
    assert champs.get("Active Devices") == "2", (
        f"Le RAID doit compter 2 disques actifs, lu : "
        f"{champs.get('Active Devices')!r}."
    )

    # L'ancienne version acceptait « State : clean » OU la présence du mot
    # « active » n'importe où dans la sortie. Comme « Active Devices » contient
    # ce mot, la seconde branche était toujours vraie et le test ne pouvait
    # pas échouer : une grappe dégradée passait (red team du 2026-09-15).
    etat = champs.get("State", "")
    assert etat, "État de la grappe illisible dans `mdadm --detail`."
    fautifs = [m for m in ("degraded", "failed", "inactive") if m in etat.lower()]
    assert not fautifs, (
        f"La grappe n'est pas saine, son état est « {etat} ». Un RAID 1 avec "
        "un disque manquant fonctionne encore : c'est précisément pour cela "
        "qu'il faut regarder l'état, pas seulement si le montage répond."
    )


def test_array_mounted(host):
    """Le RAID doit être monté sur /mnt/raid."""
    out = host.run("findmnt -n /mnt/raid")
    assert "/dev/md0" in out.stdout, "Montez /dev/md0 sur /mnt/raid (mkfs.xfs puis mount)."


def test_array_persistent(host):
    """L'array doit être déclaré dans /etc/mdadm.conf (persistance)."""
    conf = host.file("/etc/mdadm.conf")
    # mdadm --detail --scan écrit « /dev/md0 » ou « /dev/md/0 » selon la façon
    # dont la grappe a été nommée, et « /dev/md127 » si elle a été réassemblée
    # sans mdadm.conf. On accepte les trois : ce qui compte est qu'une ligne
    # ARRAY déclare la grappe, pas la forme exacte de son nom.
    assert conf.exists, (
        "Ajoutez l'array à /etc/mdadm.conf : mdadm --detail --scan >> /etc/mdadm.conf"
    )
    assert re.search(r"^ARRAY\s+/dev/md/?\d+", conf.content_string, re.MULTILINE), (
        "Aucune ligne ARRAY dans /etc/mdadm.conf. "
        "Ajoutez-la : mdadm --detail --scan >> /etc/mdadm.conf"
    )
