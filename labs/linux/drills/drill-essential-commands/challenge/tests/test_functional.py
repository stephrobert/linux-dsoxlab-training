"""Tests fonctionnels — drill-essential-commands.

5 tests = 5 tâches du drill. Chaque test vérifie l'état observable, jamais le
chemin pris par le candidat : peu importe qu'il ait utilisé find|tar, cut|sort|
uniq ou awk, seul le résultat compte.

Drill BI-DISTRIB : l'hôte n'est PAS codé en dur. `lab_target_host()` retourne
l'hôte de la target choisie (`dsoxlab check --target ubuntu`), exporté par
dsoxlab >= 0.1.7 via DSOXLAB_TARGET_HOST. Hors dsoxlab (pytest à la main, CI),
on retombe sur la target `default` du lab.yaml — d'où l'argument.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.mark.points(25)
def test_task1_archive_only_big_files(host):
    """L'archive doit contenir les fichiers > 1 Mio, et EUX SEULS."""
    assert host.file("/root/big.tar.gz").exists, (
        "/root/big.tar.gz est absent."
    )
    listing = host.check_output("tar -tzf /root/big.tar.gz")
    bases = {
        e.rsplit("/", 1)[-1]
        for e in listing.split()
        if e and not e.endswith("/")
    }
    assert {"big1.dat", "big2.dat"} <= bases, (
        "Il manque des fichiers > 1 Mio : big1.dat (2M) et big2.dat (3M) sont "
        f"attendus. Trouvés : {sorted(bases)}."
    )
    intrus = bases & {"small.txt", "tiny.log"}
    assert not intrus, (
        f"L'archive contient des fichiers qui font MOINS de 1 Mio : "
        f"{sorted(intrus)}. Le critère est la taille, pas l'extension."
    )


@pytest.mark.points(20)
def test_task2_top_user(host):
    """Le rapport doit nommer l'utilisateur le plus présent (alice, 3 lignes)."""
    f = host.file("/root/top-user.txt")
    assert f.exists, "/root/top-user.txt est absent."
    contenu = f.content_string.strip()
    assert contenu == "alice", (
        "Le fichier doit contenir le seul nom de l'utilisateur le plus "
        "fréquent d'access.csv (alice : 3 lignes, contre 2 pour bob et 1 pour "
        f"carol). Vu : {contenu!r}."
    )


@pytest.mark.points(15)
def test_task3_links(host):
    """Un lien physique (même inode) et un lien symbolique."""
    src_inode = host.check_output("stat -c %%i %s", "/srv/drill/access.csv")
    hard = host.file("/root/access.hard")
    assert hard.exists, "/root/access.hard est absent."
    assert host.check_output("stat -c %%i %s", "/root/access.hard") == src_inode, (
        "/root/access.hard n'est pas un lien PHYSIQUE vers "
        "/srv/drill/access.csv : les inodes diffèrent. Une copie ne compte pas."
    )
    soft = host.file("/root/access.soft")
    assert soft.exists, "/root/access.soft est absent."
    assert soft.is_symlink, "/root/access.soft doit être un lien SYMBOLIQUE."


@pytest.mark.points(20)
def test_task4_report_ownership_and_mode(host):
    """Le rapport doit appartenir à drilluser:drillers en 0640."""
    f = host.file("/srv/drill/report.txt")
    assert f.exists, "/srv/drill/report.txt a disparu."
    assert f.user == "drilluser", (
        f"Le propriétaire doit être drilluser (vu : {f.user})."
    )
    assert f.group == "drillers", (
        f"Le groupe doit être drillers (vu : {f.group})."
    )
    assert f.mode == 0o640, (
        "Le mode doit être 0640 : lecture/écriture pour le propriétaire, "
        "lecture pour le groupe, RIEN pour les autres — c'est un rapport "
        f"confidentiel. Vu : {oct(f.mode)}."
    )


@pytest.mark.points(20)
def test_task5_streams_are_split(host):
    """stdout et stderr doivent être séparés dans deux fichiers distincts."""
    out = host.file("/root/out.log")
    err = host.file("/root/err.log")
    assert out.exists, "/root/out.log est absent."
    assert err.exists, "/root/err.log est absent."

    out_c, err_c = out.content_string, err.content_string
    assert "ligne standard 1" in out_c and "ligne standard 2" in out_c, (
        f"/root/out.log doit contenir la sortie standard. Vu : {out_c!r}"
    )
    assert "erreur" not in out_c, (
        "/root/out.log contient des lignes d'erreur : les deux flux ont été "
        f"mélangés (2>&1 ?) au lieu d'être séparés. Vu : {out_c!r}"
    )
    assert "erreur A" in err_c and "erreur B" in err_c, (
        f"/root/err.log doit contenir la sortie d'erreur. Vu : {err_c!r}"
    )
    assert "ligne standard" not in err_c, (
        f"/root/err.log contient la sortie standard. Vu : {err_c!r}"
    )
