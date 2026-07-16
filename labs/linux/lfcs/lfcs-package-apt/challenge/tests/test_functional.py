"""Tests pytest+testinfra — lfcs-package-apt.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT (Debian) : le paquet installé, figé (hold), et l'appartenance
d'un fichier à son paquet.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "ubuntu-lfcs-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_tree_installed(host):
    """Le paquet tree doit être installé."""
    assert host.package("tree").is_installed, (
        "tree doit être installé : sudo apt-get install -y tree"
    )


def test_tree_on_hold(host):
    """tree doit être figé (hold)."""
    holds = host.check_output("apt-mark showhold").split()
    assert "tree" in holds, (
        "tree doit être figé : sudo apt-mark hold tree (vérifie apt-mark showhold)"
    )


def test_dpkg_owns_file(host):
    """dpkg doit rattacher /usr/bin/tree au paquet tree."""
    out = host.check_output("dpkg -S /usr/bin/tree")
    assert "tree" in out, (
        "dpkg -S /usr/bin/tree doit renvoyer le paquet tree."
    )
