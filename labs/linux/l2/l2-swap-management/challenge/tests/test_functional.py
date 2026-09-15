"""Tests pytest+testinfra — l2-swap-management.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` du formateur sur la VM avant les tests (mode CI). En
`dsoxlab check`, la fixture est désactivée (LAB_NO_REPLAY=1) pour tester
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
    """Le swap file doit exister et être en 0600 root:root (critère sécurité)."""
    f = host.file(SWAPFILE)
    assert f.exists, f"{SWAPFILE} doit exister : sudo dd if=/dev/zero of={SWAPFILE} bs=1M count=256"
    assert f.user == "root" and f.group == "root", (
        f"{SWAPFILE} doit appartenir à root:root (vu : {f.user}:{f.group})."
    )
    assert f.mode == 0o600, (
        f"{SWAPFILE} doit être en 0600 (vu : {oct(f.mode)}). sudo chmod 0600 {SWAPFILE}"
    )


def test_swapfile_size(host):
    """Le swap file doit faire 256 MiB, la taille demandée par l'énoncé.

    L'énoncé l'exigeait sans qu'aucun test ne le vérifie : un fichier de
    64 MiB passait la validation. On tolère une marge de 1 MiB, parce que
    `fallocate` et `dd` n'arrondissent pas de la même façon.
    """
    out = host.run(f"stat -c %s {SWAPFILE}")
    assert out.rc == 0, f"{SWAPFILE} introuvable."
    taille = int(out.stdout.strip())
    attendu = 256 * 1024 * 1024
    assert abs(taille - attendu) <= 1024 * 1024, (
        f"{SWAPFILE} doit faire 256 MiB (vu : {taille // (1024 * 1024)} MiB). "
        f"sudo dd if=/dev/zero of={SWAPFILE} bs=1M count=256"
    )


def test_swap_active(host):
    """Le swap /swapfile doit être actif."""
    out = host.run("swapon --show=NAME --noheadings 2>/dev/null")
    # Comparaison ligne à ligne : cherché en sous-chaîne, « /swapfile » serait
    # trouvé dans un « /swapfile2 » resté d'un autre essai.
    actifs = [x.strip() for x in out.stdout.splitlines() if x.strip()]
    assert SWAPFILE in actifs, (
        f"{SWAPFILE} doit être actif. Après mkswap : sudo swapon {SWAPFILE}. "
        f"Swaps actifs : {actifs or 'aucun'}."
    )


def test_swap_persistent_fstab(host):
    """L'entrée swap doit figurer dans /etc/fstab (persistance reboot)."""
    fstab = host.file("/etc/fstab").content_string
    has_line = any(
        SWAPFILE in line and "swap" in line and not line.lstrip().startswith("#")
        for line in fstab.splitlines()
    )
    assert has_line, (
        "Ajoutez une entrée swap pour /swapfile dans /etc/fstab : "
        "/swapfile none swap sw 0 0"
    )


def test_swappiness_is_ten(host):
    """vm.swappiness doit valoir 10, et le rester après un redémarrage."""
    out = host.run("sysctl -n vm.swappiness")
    assert out.stdout.strip() == "10", (
        f"vm.swappiness doit valoir 10 (vu : {out.stdout.strip()}). "
        "Posez-le dans /etc/sysctl.d/99-swappiness.conf puis sysctl -p."
    )

    # Le titre de ce test promet une règle DURABLE. Sans cette seconde moitié,
    # il ne mesurait que la valeur courante : un `sysctl -w vm.swappiness=10`,
    # qui disparaît au redémarrage, le validait (red team du 2026-09-15).
    declaree = host.run(
        "grep -rqs '^[[:space:]]*vm\\.swappiness[[:space:]]*=' "
        "/etc/sysctl.conf /etc/sysctl.d/ /usr/lib/sysctl.d/"
    )
    assert declaree.rc == 0, (
        "vm.swappiness vaut bien 10, mais aucun fichier de /etc/sysctl.d/ ne "
        "le déclare : la valeur a été posée à la main et disparaîtra au "
        "premier redémarrage. Écrivez-la dans "
        "/etc/sysctl.d/99-swappiness.conf."
    )
