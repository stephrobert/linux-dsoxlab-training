"""Tests pytest+testinfra — l3-grub-kernel-args.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT du bootloader : le paramètre sur le noyau par défaut (grubby)
ET dans /etc/default/grub (persistance des futurs noyaux).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_default_kernel_has_param(host):
    """Le noyau par défaut doit avoir panic=10 dans ses arguments."""
    info = host.check_output("grubby --info=DEFAULT")
    assert "panic=10" in info, (
        "panic=10 doit être sur le noyau par défaut : "
        'grubby --update-kernel=ALL --args="panic=10"'
    )


def test_default_grub_persists_param(host):
    """/etc/default/grub doit contenir panic=10 (futurs noyaux)."""
    grub = host.file("/etc/default/grub").content_string
    assert "panic=10" in grub, (
        "panic=10 doit être dans GRUB_CMDLINE_LINUX de /etc/default/grub, "
        "sinon perdu à la prochaine mise à jour du noyau."
    )
