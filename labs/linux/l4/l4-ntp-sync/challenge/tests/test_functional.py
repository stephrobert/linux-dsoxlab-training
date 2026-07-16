"""Tests pytest+testinfra — l4-ntp-sync.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : fuseau, NTP activé, et chronyd actif ET enabled
(persistance après reboot).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_timezone(host):
    """Le fuseau doit être Europe/Paris."""
    tz = host.check_output("timedatectl show -p Timezone --value").strip()
    assert tz == "Europe/Paris", (
        f"Fuseau attendu Europe/Paris (vu : {tz!r}). "
        "timedatectl set-timezone Europe/Paris"
    )


def test_ntp_enabled(host):
    """Le NTP doit être activé via timedatectl."""
    ntp = host.check_output("timedatectl show -p NTP --value").strip()
    assert ntp == "yes", (
        f"NTP attendu 'yes' (vu : {ntp!r}). timedatectl set-ntp true"
    )


def test_chronyd_running_and_enabled(host):
    """chronyd doit tourner ET être enabled (persistance reboot)."""
    svc = host.service("chronyd")
    assert svc.is_running, "chronyd doit tourner : systemctl start chronyd"
    assert svc.is_enabled, (
        "chronyd doit être enabled (sinon perdu au reboot) : "
        "systemctl enable chronyd"
    )
