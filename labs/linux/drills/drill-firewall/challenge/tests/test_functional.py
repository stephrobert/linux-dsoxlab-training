"""Tests fonctionnels — drill-firewall.

5 tests = 5 tâches. Drill BI-DISTRIB À OUTIL VARIABLE : firewalld sur RHEL, ufw
sur Debian. Les assertions se conditionnent sur la distribution réelle, jamais
sur l'outil que le candidat a tapé.

La PERSISTANCE n'est pas une tâche séparée — elle serait offerte sur ufw, qui
persiste par défaut. À la place, une fixture RECHARGE le pare-feu avant les
tests : une règle firewalld posée sans --permanent disparaît à ce moment-là.
Le piège RHCSA est ainsi intégré aux tâches, pas annoncé dans le sujet.

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
    return host.system_info.distribution.lower() in ("ubuntu", "debian")


@pytest.fixture(scope="module", autouse=True)
def _reload_firewall(host):
    """Recharge le pare-feu AVANT les tests : ce qui n'est pas persistant meurt.

    C'est ce qui rend la persistance vérifiable sans en faire une tâche à part.
    Le rechargement ne coupe pas les connexions déjà établies, donc la session
    SSH des tests survit.
    """
    if _is_debian(host):
        host.run("ufw reload")
    else:
        host.run("firewall-cmd --reload")


@pytest.mark.points(20)
def test_task1_firewall_is_up(host):
    """Le pare-feu doit être actif — et le rester au reboot."""
    if _is_debian(host):
        statut = host.check_output("ufw status")
        assert "Status: active" in statut, (
            f"ufw n'est pas actif. Vu :\n{statut}"
        )
    else:
        svc = host.service("firewalld")
        assert svc.is_running, "firewalld n'est pas démarré."
        assert svc.is_enabled, (
            "firewalld n'est pas enabled : le pare-feu ne reviendrait pas au "
            "reboot, la machine redémarrerait sans protection."
        )


@pytest.mark.points(20)
def test_task2_http_port_open(host):
    """80/tcp doit être ouvert — et avoir SURVÉCU au rechargement."""
    if _is_debian(host):
        statut = host.check_output("ufw status")
        assert "80/tcp" in statut, (
            f"Le port 80/tcp n'est pas autorisé. Vu :\n{statut}"
        )
    else:
        ports = host.check_output("firewall-cmd --list-all")
        assert "80/tcp" in ports or "http" in ports, (
            "Le port 80/tcp n'est pas ouvert APRÈS un rechargement : la règle "
            "a été posée sans --permanent, elle n'a pas survécu. "
            f"Vu :\n{ports}"
        )


@pytest.mark.points(20)
def test_task3_app_port_open(host):
    """8443/tcp doit être ouvert — et avoir SURVÉCU au rechargement."""
    if _is_debian(host):
        statut = host.check_output("ufw status")
        assert "8443/tcp" in statut, (
            f"Le port 8443/tcp n'est pas autorisé. Vu :\n{statut}"
        )
    else:
        ports = host.check_output("firewall-cmd --list-all")
        assert "8443/tcp" in ports, (
            "Le port 8443/tcp n'est pas ouvert APRÈS un rechargement : règle "
            f"non permanente. Vu :\n{ports}"
        )


@pytest.mark.points(20)
def test_task4_ssh_still_allowed(host):
    """SSH doit rester autorisé — sinon on perd la machine."""
    if _is_debian(host):
        statut = host.check_output("ufw status")
        assert "OpenSSH" in statut or "22/tcp" in statut, (
            f"SSH n'est plus autorisé : la machine deviendrait injoignable au "
            f"prochain redémarrage du pare-feu. Vu :\n{statut}"
        )
    else:
        regles = host.check_output("firewall-cmd --list-all")
        assert "ssh" in regles or "22/tcp" in regles, (
            f"SSH n'est plus autorisé. Vu :\n{regles}"
        )


@pytest.mark.points(20)
def test_task5_telnet_rejected(host):
    """23/tcp doit être explicitement rejeté."""
    if _is_debian(host):
        statut = host.check_output("ufw status")
        ligne = next(
            (entree for entree in statut.splitlines() if "23/tcp" in entree), ""
        )
        assert ligne, f"Aucune règle ne vise 23/tcp. Vu :\n{statut}"
        assert "DENY" in ligne.upper() or "REJECT" in ligne.upper(), (
            f"23/tcp doit être explicitement refusé, pas autorisé. Vu : {ligne!r}"
        )
    else:
        regles = host.check_output("firewall-cmd --list-all")
        ligne = next(
            (
                entree
                for entree in regles.splitlines()
                if 'port="23"' in entree or "port=23" in entree
            ),
            "",
        )
        assert ligne, (
            "Aucune règle riche ne vise le port 23. Une règle riche de rejet "
            f"est attendue. Vu :\n{regles}"
        )
        # Viser le port ne suffit pas : il faut le REJETER. Sans ce contrôle,
        # une règle riche « accept » sur le port 23 marquait les 20 points de
        # la tâche « Telnet, jamais », en ouvrant précisément ce qu'elle
        # demande de fermer.
        assert "reject" in ligne.lower() or "drop" in ligne.lower(), (
            "La règle riche vise bien 23/tcp mais ne le rejette pas. "
            "L'énoncé demande un rejet explicite, pas une simple mention du "
            f"port. Vu : {ligne!r}"
        )
        assert "reject" in regles or "drop" in regles, (
            f"Le port 23 doit être rejeté, pas autorisé. Vu :\n{regles}"
        )
