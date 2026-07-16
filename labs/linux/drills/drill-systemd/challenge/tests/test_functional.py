"""Tests fonctionnels — drill-systemd.

5 tests = 5 tâches. On vérifie l'état observable via systemd lui-même
(`systemctl show`), pas le contenu des fichiers : ce qui compte est la config
EFFECTIVE, pas ce qui est écrit dans l'unité.

Drill BI-DISTRIB : hôte non codé en dur (`lab_target_host()`, dsoxlab >= 0.1.7).
Deux pièges sondés sur les deux distribs et neutralisés :
  - le service cron s'appelle crond (alma) ou cron (ubuntu) : on ne teste que
    la crontab, jamais le nom du service ;
  - la cible par défaut diffère au départ : le setup la normalise à graphical.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _show(host, unit: str, prop: str) -> str:
    """Valeur EFFECTIVE d'une propriété systemd (pas le fichier d'unité)."""
    out = host.check_output("systemctl show %s --property=%s", unit, prop)
    return out.split("=", 1)[1] if "=" in out else ""


@pytest.mark.points(20)
def test_task1_service_with_restart_policy(host):
    """labapi : activée, démarrée, et redémarrant en cas d'échec."""
    svc = host.service("labapi")
    assert svc.is_enabled, (
        "labapi.service n'est pas enabled : elle ne reviendrait pas au reboot."
    )
    assert svc.is_running, "labapi.service n'est pas démarrée."
    restart = _show(host, "labapi.service", "Restart")
    assert restart == "on-failure", (
        "labapi.service doit redémarrer en cas d'échec (Restart=on-failure). "
        f"Vu : {restart!r}."
    )


@pytest.mark.points(20)
def test_task2_weekly_timer(host):
    """labclean.timer : activé, actif, déclenché le lundi à 04:00."""
    timer = host.service("labclean.timer")
    assert timer.is_enabled, "labclean.timer n'est pas enabled."
    assert timer.is_running, "labclean.timer n'est pas actif."
    cal = _show(host, "labclean.timer", "TimersCalendar")
    assert "04:00" in cal, (
        f"Le timer doit se déclencher à 04:00. Vu : {cal!r}"
    )
    assert "Mon" in cal, (
        f"Le timer doit se déclencher le lundi (Mon). Vu : {cal!r}"
    )
    unit = host.file("/etc/systemd/system/labclean.service")
    assert unit.exists, "L'unité labclean.service est absente."
    assert "labclean.sh" in unit.content_string, (
        "labclean.service doit exécuter /usr/local/bin/labclean.sh."
    )


@pytest.mark.points(20)
def test_task3_cron_job(host):
    """opsuser doit avoir une tâche cron toutes les 15 minutes."""
    cron = host.check_output("crontab -u opsuser -l 2>/dev/null || true")
    assert "labclean.sh" in cron, (
        f"Aucune tâche cron d'opsuser n'appelle labclean.sh. Vu : {cron!r}"
    )
    ligne = next(
        (ligne for ligne in cron.splitlines()
         if "labclean.sh" in ligne and not ligne.strip().startswith("#")),
        "",
    )
    assert ligne.split()[0] == "*/15", (
        "La tâche doit tourner toutes les 15 minutes (*/15 en champ minute). "
        f"Vu : {ligne!r}"
    )


@pytest.mark.points(20)
def test_task4_default_boot_target(host):
    """La cible de démarrage par défaut doit être multi-user (pas graphical)."""
    cible = host.check_output("systemctl get-default")
    assert cible == "multi-user.target", (
        "Un serveur ne doit pas démarrer en graphical.target : la cible par "
        f"défaut doit être multi-user.target. Vu : {cible!r}."
    )


@pytest.mark.points(20)
def test_task5_service_masked(host):
    """labdanger doit être MASQUÉ : disable ne suffit pas."""
    etat = host.run("systemctl is-enabled labdanger.service").stdout.strip()
    assert etat == "masked", (
        "labdanger.service doit être MASQUÉ. Un simple disable le laisserait "
        "démarrable à la main ou par dépendance ; le masquage le lie à "
        f"/dev/null. Vu : {etat!r}."
    )
    # Preuve : même un démarrage explicite doit échouer.
    res = host.run("systemctl start labdanger.service")
    assert res.rc != 0, (
        "labdanger.service a démarré alors qu'il devait être masqué."
    )
