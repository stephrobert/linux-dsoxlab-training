"""Tests pytest+testinfra — l3-service-create-unit.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le service est actif ET activé au boot, et il fait
réellement son travail (le programme a tourné) — pas juste que l'unit existe.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"
SERVICE = "labapp"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_service_active(host):
    """Le service labapp doit être actif (running)."""
    assert host.service(SERVICE).is_running, message(
        en="labapp.service must be started: systemctl start labapp "
        "(after writing the unit and running daemon-reload).",
        fr="labapp.service doit être démarré : systemctl start labapp "
        "(après avoir écrit l'unit et fait daemon-reload).",
    )


def test_service_enabled(host):
    """Le service doit être activé au boot (persistance)."""
    assert host.service(SERVICE).is_enabled, message(
        en="labapp.service must be enabled at boot: systemctl enable labapp "
        "(or enable --now).",
        fr="labapp.service doit être activé au démarrage : systemctl enable labapp "
        "(ou enable --now).",
    )


def test_service_did_its_job(host):
    """Le programme du service a réellement tourné (marqueur écrit)."""
    f = host.file("/run/labapp.status")
    assert f.exists and "running" in f.content_string, message(
        en="/run/labapp.status must contain 'running': the service must really "
        "run /usr/local/bin/labapp.sh (the right ExecStart).",
        fr="/run/labapp.status doit contenir 'running' : le service doit vraiment "
        "exécuter /usr/local/bin/labapp.sh (bon ExecStart).",
    )
