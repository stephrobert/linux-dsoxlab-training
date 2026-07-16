"""Tests pytest+testinfra — l3-scheduling-at.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : atd actif, une tâche at en file, et son script planifie bien
la commande attendue.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_atd_running(host):
    """atd doit tourner pour gérer les tâches at."""
    assert host.service("atd").is_running, (
        "atd doit tourner : systemctl enable --now atd"
    )


def test_job_queued(host):
    """Une tâche at doit être en file (atq non vide)."""
    queue = host.check_output("atq").strip()
    assert queue, (
        "Aucune tâche at en file (atq est vide). "
        "echo 'touch /run/rapport.done' | at now + 1 hour"
    )


def test_job_schedules_command(host):
    """Une tâche en file doit planifier 'touch /run/rapport.done'."""
    ids = [
        line.split()[0]
        for line in host.check_output("atq").splitlines()
        if line.strip()
    ]
    scripts = " ".join(host.check_output("at -c %s", jid) for jid in ids)
    assert "touch /run/rapport.done" in scripts, (
        "Aucune tâche at ne planifie 'touch /run/rapport.done'. "
        "Vérifie avec at -c <numéro>."
    )
