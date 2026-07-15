"""Tests pytest+testinfra — l2-package-management.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT logiciel réel (base RPM), pas la commande tapée : tree présent,
zip absent, et la commande tree utilisable.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_tree_installed(host):
    """Le paquet tree doit être installé."""
    assert host.package("tree").is_installed, (
        "Le paquet 'tree' doit être installé : sudo dnf install -y tree"
    )


def test_zip_removed(host):
    """Le paquet zip doit avoir été retiré."""
    assert not host.package("zip").is_installed, (
        "Le paquet 'zip' doit être retiré : sudo dnf remove -y zip"
    )


def test_tree_command_available(host):
    """La commande tree doit être utilisable (le paquet fournit bien le binaire)."""
    assert host.run("command -v tree").rc == 0, (
        "La commande 'tree' doit être disponible après installation."
    )
