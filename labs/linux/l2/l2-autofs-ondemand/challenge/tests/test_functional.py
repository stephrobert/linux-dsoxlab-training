"""Tests pytest+testinfra — l2-autofs-ondemand.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : autofs tourne, les cartes existent, et surtout accéder à
/autofs/data DÉCLENCHE réellement le montage du bon disque (le témoin est
lisible) *par autofs*, et non par un mount posé à la main. C'est le comportement
à la demande, pas juste la config.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"
MOUNT_POINT = "/autofs"
KEY = "/autofs/data"
# Témoin écrit par setup.yaml sur le XFS du disque supplémentaire : sa présence
# prouve que c'est bien CE filesystem qui a été monté.
MARKER = "monte par autofs"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.mark.garde_fou
def test_autofs_running(host):
    """Le service autofs doit tourner."""
    assert host.service("autofs").is_running, message(
        en="autofs must be started: systemctl enable --now autofs",
        fr="autofs doit être démarré : systemctl enable --now autofs",
    )


def test_master_map(host):
    """La carte maître doit associer /autofs à une carte de montage.

    L'énoncé ne dicte pas le NOM du fichier : on accepte /etc/auto.master
    comme n'importe quel fichier de /etc/auto.master.d/. La ligne doit être
    active (une ligne commentée ne compte pas).
    """
    declared = host.run(
        "grep -rhs -e '^[[:space:]]*/autofs' "
        "/etc/auto.master /etc/auto.master.d/"
    ).stdout.strip()
    assert declared, message(
        en="No active master map declares /autofs. Create "
        "/etc/auto.master.d/lab.autofs: /autofs  /etc/auto.lab",
        fr="Aucune carte maître active ne déclare /autofs. Crée "
        "/etc/auto.master.d/lab.autofs : /autofs  /etc/auto.lab",
    )


def test_mount_map(host):
    """La carte de montage doit décrire la clé 'data' en xfs."""
    f = host.file("/etc/auto.lab")
    assert f.exists, message(
        en="The mount map /etc/auto.lab is missing.",
        fr="La carte de montage /etc/auto.lab manque.",
    )
    content = f.content_string
    assert "data" in content and "xfs" in content, message(
        en="The map /etc/auto.lab must describe 'data' with fstype xfs pointing at the "
        f"disk. Seen:\n{content}",
        fr="La carte /etc/auto.lab doit décrire 'data' en fstype xfs vers le "
        f"disque. Vu :\n{content}",
    )


def test_ondemand_mount_works(host):
    """Accéder à /autofs/data doit DÉCLENCHER le montage et servir le témoin.

    Trois preuves distinctes, dans cet ordre :

    1. l'accès rend le témoin du disque lisible (le montage s'est produit) ;
    2. /autofs est un point de montage de type ``autofs`` (c'est donc bien
       l'automonteur qui gère le chemin, et non un ``mount`` posé à la main) ;
    3. ce que l'accès a monté sous la clé est bien le XFS du disque.

    Les trois lectures sont faites séparément : une commande unique dont la
    sortie contient le chemin ``/autofs`` rendait l'assertion « autofs dans la
    sortie » toujours vraie, y compris sur le message d'erreur de ``cat``.
    """
    # 1. C'est cet accès qui déclenche le montage.
    marker = host.run("cat /autofs/data/marker.txt 2>&1")
    assert MARKER in marker.stdout, message(
        en=f"Accessing {KEY} must mount the disk and make marker.txt readable "
        f"(on-demand automount). Got:\n{marker.stdout or marker.stderr}",
        fr=f"Accéder à {KEY} doit monter le disque et rendre marker.txt lisible "
        f"(automontage à la demande). Obtenu :\n{marker.stdout or marker.stderr}",
    )

    # 2. Le chemin est géré par l'automonteur, pas monté à la main.
    parent = host.run("findmnt -no FSTYPE %s", MOUNT_POINT).stdout.strip()
    assert parent == "autofs", message(
        en=f"{MOUNT_POINT} must be a mount point of type 'autofs': without "
        "that, the mount is not on demand, it is a static mount. "
        f"findmnt sees {parent!r} there.",
        fr=f"{MOUNT_POINT} doit être un point de montage de type 'autofs' : sans "
        "cela le montage n'est pas à la demande, c'est un mount statique. "
        f"findmnt y voit {parent!r}.",
    )

    # 3. Et le filesystem monté sous la clé est bien le XFS du disque.
    fstype = host.run("findmnt -no FSTYPE %s", KEY).stdout.strip()
    assert fstype == "xfs", message(
        en=f"{KEY} must be mounted as xfs once triggered. Seen: {fstype!r}.",
        fr=f"{KEY} doit être monté en xfs une fois déclenché. Vu : {fstype!r}.",
    )
