"""Tests fonctionnels — drill-apparmor.

4 tests = 4 tâches. Drill MONO-DISTRIB (LFCS) : AppArmor n'a pas d'équivalent
RHEL, RHCSA a drill-selinux.

On interroge aa-status --json, la source de vérité du noyau — pas les fichiers
de profil. Les clés ne sont PAS uniformes (sondé sur la VM) : 'ping' et
'tcpdump' sont des noms courts, man est '/usr/bin/man'.
"""
from __future__ import annotations

import json

import pytest

from conftest import lab_host, lab_target_host

TARGET_HOST = lab_target_host("ubuntu-lfcs-1.lab")


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module")
def profils(host):
    """Les profils chargés et leur mode, vus par le noyau."""
    return json.loads(host.check_output("aa-status --json"))["profiles"]


@pytest.mark.points(25)
def test_task1_apparmor_is_up(host, profils):
    """AppArmor doit être actif et charger ses profils."""
    svc = host.service("apparmor")
    assert svc.is_enabled, (
        "Le service apparmor n'est pas enabled : la protection ne reviendrait "
        "pas au reboot."
    )
    assert len(profils) > 0, (
        "Aucun profil AppArmor n'est chargé : le MAC ne protège rien."
    )


@pytest.mark.points(25)
def test_task2_ping_in_complain(host, profils):
    """ping doit être en mode PLAINTE (journalise sans bloquer)."""
    mode = profils.get("ping")
    assert mode is not None, (
        f"Le profil ping n'est pas chargé. Profils vus : {len(profils)}."
    )
    assert mode == "complain", (
        "Le profil ping doit être en mode complain : il journalise les "
        f"violations sans les bloquer. Vu : {mode!r}."
    )


@pytest.mark.points(25)
def test_task3_man_in_enforce(host, profils):
    """man doit être en mode APPLICATION (bloque réellement)."""
    mode = profils.get("/usr/bin/man")
    assert mode is not None, (
        "Le profil /usr/bin/man n'est pas chargé."
    )
    assert mode == "enforce", (
        "Le profil /usr/bin/man doit être en mode enforce : en complain il "
        f"journalise mais ne bloque rien. Vu : {mode!r}."
    )


@pytest.mark.points(25)
def test_task4_tcpdump_in_enforce(host, profils):
    """tcpdump doit être en mode APPLICATION."""
    mode = profils.get("tcpdump")
    assert mode is not None, "Le profil tcpdump n'est pas chargé."
    assert mode == "enforce", (
        f"Le profil tcpdump doit être en mode enforce. Vu : {mode!r}."
    )
