"""Tests pytest+testinfra — l3-scheduling-cron.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : une planification cron réelle (peu importe le mécanisme :
/etc/cron.d, /etc/crontab, crontab utilisateur) qui lance report.sh à 02:30.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module")
def cron_lines(host) -> list[str]:
    # Rassemble toutes les sources cron possibles.
    out = host.check_output(
        "cat /etc/crontab /etc/cron.d/* /var/spool/cron/* "
        "/var/spool/cron/crontabs/* 2>/dev/null || true"
    )
    return [
        ln.strip()
        for ln in out.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def _report_line(cron_lines: list[str]) -> str | None:
    for ln in cron_lines:
        if "report.sh" in ln:
            return ln
    return None


def test_schedule_exists(cron_lines):
    """Une entrée cron doit lancer /usr/local/bin/report.sh."""
    assert _report_line(cron_lines) is not None, (
        "Aucune entrée cron ne lance report.sh. Ajoute une planification "
        "(ex. /etc/cron.d/report)."
    )


def test_schedule_is_daily_0230(cron_lines):
    """La planification doit être 02:30 chaque jour (minute 30, heure 2)."""
    line = _report_line(cron_lines)
    assert line is not None, "Entrée cron pour report.sh absente."
    fields = line.split()
    assert len(fields) >= 5, f"Ligne cron mal formée : {line!r}"
    minute, hour, dom, mon, dow = fields[:5]
    assert minute == "30" and hour == "2", (
        f"La tâche doit tourner à 02:30 (minute 30, heure 2), vu minute={minute} "
        f"heure={hour}. Format : 30 2 * * *"
    )
    assert dom == "*" and mon == "*" and dow == "*", (
        f"« Chaque jour » = jour/mois/jour-semaine à * (vu : {dom} {mon} {dow})."
    )
