"""Tests pytest+testinfra — l3-scheduling-timers.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : les unités sur disque (avec OnCalendar), et le timer activé
(persistance reboot) ET actif.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_units_on_disk(host):
    """Le service et le timer doivent exister sous /etc/systemd/system."""
    for unit in ("labbackup.service", "labbackup.timer"):
        f = host.file(f"/etc/systemd/system/{unit}")
        assert f.exists, f"/etc/systemd/system/{unit} doit exister."


def test_timer_has_oncalendar(host):
    """Le timer doit déclarer un planning OnCalendar."""
    timer = host.file("/etc/systemd/system/labbackup.timer").content_string
    assert "OnCalendar" in timer, (
        "labbackup.timer doit avoir un OnCalendar= dans sa section [Timer]."
    )


def test_timer_enabled_and_active(host):
    """labbackup.timer doit être enabled (persistance) ET actif."""
    timer = host.service("labbackup.timer")
    assert timer.is_enabled, (
        "labbackup.timer doit être enabled (sinon perdu au reboot) : "
        "systemctl enable labbackup.timer"
    )
    assert timer.is_running, (
        "labbackup.timer doit être actif : systemctl start labbackup.timer"
    )
