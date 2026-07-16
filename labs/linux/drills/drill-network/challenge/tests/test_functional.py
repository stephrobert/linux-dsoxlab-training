"""Tests fonctionnels — drill-network.

4 tests = 4 tâches. Drill BI-DISTRIB À OUTIL VARIABLE : nmcli sur RHEL, netplan
sur Debian. On lit l'état du NOYAU (ip addr / ip route / ip link), jamais les
fichiers de config : peu importe l'outil employé, seul le résultat compte.

La persistance est vérifiée sans en faire une tâche à part : la fixture
RECHARGE le réseau avant les tests. Un `ip addr add` posé à la main disparaît à
ce moment-là — c'est le piège, intégré plutôt qu'annoncé.

On ne touche JAMAIS l'interface de gestion : son nom varie selon le provider et
la distrib, et la couper ferait perdre la machine.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")
IFACE = "lab0"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _is_debian(host) -> bool:
    return host.system_info.distribution.lower() in ("ubuntu", "debian")


@pytest.fixture(scope="module", autouse=True)
def _reload_network(host):
    """Recharge le réseau : ce qui n'est pas déclaré sur disque meurt ici.

    On ne recharge que lab0 côté RHEL — jamais l'interface de gestion, sinon
    on couperait la session SSH des tests eux-mêmes.
    """
    if _is_debian(host):
        host.run("netplan apply")
    else:
        host.run("nmcli con reload")
        host.run("nmcli con up lab0")


@pytest.mark.points(25)
def test_task1_static_address(host):
    """lab0 doit porter 203.0.113.20/24 APRÈS un rechargement."""
    out = host.check_output("ip -4 addr show %s 2>/dev/null || true", IFACE)
    assert "203.0.113.20" in out, (
        f"{IFACE} ne porte pas 203.0.113.20 après un rechargement du réseau : "
        "l'adresse n'a pas été déclarée de façon persistante (un ip addr add "
        f"ne survit pas). Vu :\n{out}"
    )


@pytest.mark.points(25)
def test_task2_static_route(host):
    """La route vers 192.0.2.0/24 doit être active APRÈS un rechargement."""
    routes = host.check_output("ip route show")
    ligne = next(
        (entree for entree in routes.splitlines() if "192.0.2.0/24" in entree), ""
    )
    assert ligne, (
        f"La route vers 192.0.2.0/24 est absente après un rechargement. "
        f"Vu :\n{routes}"
    )
    assert "203.0.113.1" in ligne, (
        f"La route doit passer via 203.0.113.1. Vu : {ligne!r}"
    )


@pytest.mark.points(25)
def test_task3_mtu(host):
    """lab0 doit porter un MTU de 1400 APRÈS un rechargement."""
    out = host.check_output("ip link show %s", IFACE)
    assert "mtu 1400" in out, (
        f"{IFACE} doit porter un MTU de 1400, déclaré de façon persistante. "
        f"Vu :\n{out}"
    )


@pytest.mark.points(25)
def test_task4_name_resolution(host):
    """lab-net.lab doit résoudre localement vers 203.0.113.20."""
    out = host.check_output("getent hosts lab-net.lab || true")
    assert "203.0.113.20" in out, (
        "Le nom lab-net.lab ne résout pas vers 203.0.113.20. Aucun DNS n'est "
        f"disponible : c'est /etc/hosts qui doit le déclarer. Vu : {out!r}"
    )
