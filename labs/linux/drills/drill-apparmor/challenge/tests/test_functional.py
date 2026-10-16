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

from conftest import lab_host, lab_target_host, message

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
    assert svc.is_enabled, message(
        en="The apparmor service is not enabled: the protection would not come "
        "back at reboot.",
        fr="Le service apparmor n'est pas enabled : la protection ne reviendrait "
        "pas au reboot.",
    )
    assert len(profils) > 0, message(
        en="No AppArmor profile is loaded: MAC protects nothing.",
        fr="Aucun profil AppArmor n'est chargé : le MAC ne protège rien.",
    )


@pytest.mark.points(25)
def test_task2_ping_in_complain(host, profils):
    """ping doit être en mode PLAINTE (journalise sans bloquer)."""
    mode = profils.get("ping")
    assert mode is not None, message(
        en=f"The ping profile is not loaded. Profiles seen: {len(profils)}.",
        fr=f"Le profil ping n'est pas chargé. Profils vus : {len(profils)}.",
    )
    assert mode == "complain", message(
        en="The ping profile must be in complain mode: it logs "
        f"violations without blocking them. Seen: {mode!r}.",
        fr="Le profil ping doit être en mode complain : il journalise les "
        f"violations sans les bloquer. Vu : {mode!r}.",
    )


@pytest.mark.points(25)
def test_task3_man_in_enforce(host, profils):
    """man doit être en mode APPLICATION (bloque réellement)."""
    mode = profils.get("/usr/bin/man")
    assert mode is not None, message(
        en="The /usr/bin/man profile is not loaded.",
        fr="Le profil /usr/bin/man n'est pas chargé.",
    )
    assert mode == "enforce", message(
        en="The /usr/bin/man profile must be in enforce mode: in complain it "
        f"logs but blocks nothing. Seen: {mode!r}.",
        fr="Le profil /usr/bin/man doit être en mode enforce : en complain il "
        f"journalise mais ne bloque rien. Vu : {mode!r}.",
    )


@pytest.mark.points(25)
def test_task4_tcpdump_in_enforce(host, profils):
    """tcpdump doit être en mode APPLICATION."""
    mode = profils.get("tcpdump")
    assert mode is not None, message(
        en="The tcpdump profile is not loaded.",
        fr="Le profil tcpdump n'est pas chargé.",
    )
    assert mode == "enforce", message(
        en=f"The tcpdump profile must be in enforce mode. Seen: {mode!r}.",
        fr=f"Le profil tcpdump doit être en mode enforce. Vu : {mode!r}.",
    )
