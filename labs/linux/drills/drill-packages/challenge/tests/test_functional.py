"""Tests fonctionnels — drill-packages.

5 tests = 5 tâches. Drill BI-DISTRIB À OUTIL VARIABLE : l'objectif est commun
aux deux certifications, seul l'outil diffère. Les assertions se conditionnent
donc sur la distribution réelle de l'hôte, jamais sur l'outil employé par le
candidat — qu'il ait tapé `dnf`, `yum`, `apt` ou `apt-get` n'entre pas en ligne
de compte : seul l'état du système est jugé.

Hôte non codé en dur (`lab_target_host()`, dsoxlab >= 0.1.7).
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _is_debian(host) -> bool:
    """La famille de la distribution, pour choisir la bonne vérification."""
    return host.system_info.distribution.lower() in ("ubuntu", "debian")


@pytest.mark.points(20)
def test_task1_package_installed(host):
    """tree doit être installé — quel que soit l'outil employé."""
    assert host.package("tree").is_installed, (
        "Le paquet tree n'est pas installé."
    )


@pytest.mark.points(20)
def test_task2_package_frozen(host):
    """tree doit être gelé : aucune mise à jour ne doit pouvoir le bouger."""
    if _is_debian(host):
        gel = host.check_output("apt-mark showhold")
        assert "tree" in gel.split(), (
            "tree n'est pas gelé : apt-mark showhold ne le liste pas. "
            f"Vu : {gel!r}"
        )
    else:
        gel = host.check_output("dnf versionlock list 2>/dev/null || true")
        assert "tree" in gel, (
            "tree n'est pas gelé : dnf versionlock list ne le liste pas. "
            f"Vu : {gel!r}"
        )


@pytest.mark.points(20)
def test_task3_which_package_owns_ssh(host):
    """/root/owner.txt doit nommer le paquet qui fournit /usr/bin/ssh."""
    f = host.file("/root/owner.txt")
    assert f.exists, "/root/owner.txt est absent."
    contenu = f.content_string.strip()
    # openssh-clients (RHEL) et openssh-client (Debian) : la sous-chaîne
    # commune suffit et évite de brancher pour rien.
    assert "openssh-client" in contenu, (
        "Le fichier doit nommer le paquet qui fournit /usr/bin/ssh "
        "(openssh-clients sur RHEL, openssh-client sur Debian). "
        f"Vu : {contenu!r}"
    )


@pytest.mark.points(20)
def test_task4_files_of_package(host):
    """/root/tree-files.txt doit lister les fichiers installés par tree."""
    f = host.file("/root/tree-files.txt")
    assert f.exists, "/root/tree-files.txt est absent."
    contenu = f.content_string
    assert "/usr/bin/tree" in contenu, (
        "La liste doit contenir les fichiers réellement installés par tree, "
        f"dont /usr/bin/tree. Vu :\n{contenu[:300]}"
    )


@pytest.mark.points(20)
def test_task5_package_removed(host):
    """nano doit avoir été supprimé."""
    assert not host.package("nano").is_installed, (
        "Le paquet nano est toujours installé."
    )
