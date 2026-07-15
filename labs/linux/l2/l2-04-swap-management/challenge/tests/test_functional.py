"""Tests pytest+testinfra — l2-04-swap-management.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` du formateur sur la VM avant les tests (mode CI). En
`dsoxlab check`, la fixture est desactivee (LAB_NO_REPLAY=1) pour tester
le travail manuel de l'apprenant.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
SWAPFILE = "/swapfile"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_swapfile_exists_and_secure(host):
    """Le swap file doit exister et etre en 0600 root:root (critere securite)."""
    f = host.file(SWAPFILE)
    assert f.exists, f"{SWAPFILE} doit exister : sudo dd if=/dev/zero of={SWAPFILE} bs=1M count=256"
    assert f.user == "root" and f.group == "root", (
        f"{SWAPFILE} doit appartenir a root:root (vu : {f.user}:{f.group})."
    )
    assert f.mode == 0o600, (
        f"{SWAPFILE} doit etre en 0600 (vu : {oct(f.mode)}). sudo chmod 0600 {SWAPFILE}"
    )


def test_swap_active(host):
    """Le swap /swapfile doit etre actif."""
    out = host.run("swapon --show=NAME --noheadings 2>/dev/null")
    assert SWAPFILE in out.stdout, (
        f"{SWAPFILE} doit etre actif. Apres mkswap : sudo swapon {SWAPFILE}"
    )


def test_swap_persistent_fstab(host):
    """L'entree swap doit figurer dans /etc/fstab (persistance reboot)."""
    fstab = host.file("/etc/fstab").content_string
    has_line = any(
        SWAPFILE in line and "swap" in line and not line.lstrip().startswith("#")
        for line in fstab.splitlines()
    )
    assert has_line, (
        "Ajoutez une entree swap pour /swapfile dans /etc/fstab : "
        "/swapfile none swap sw 0 0"
    )


def test_swappiness_is_ten(host):
    """vm.swappiness doit valoir 10 (regle durable)."""
    out = host.run("sysctl -n vm.swappiness")
    assert out.stdout.strip() == "10", (
        f"vm.swappiness doit valoir 10 (vu : {out.stdout.strip()}). "
        "Posez-le dans /etc/sysctl.d/99-swappiness.conf puis sysctl -p."
    )
