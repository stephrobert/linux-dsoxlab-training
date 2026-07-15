"""Tests pytest+testinfra — l3-process-signals-priority.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la priorité RÉELLE du processus du service (ps -o ni), pas
juste la config — le service tourne bien à nice 10.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
SERVICE = "labworker"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_service_running(host):
    """Le service labworker doit tourner."""
    assert host.service(SERVICE).is_running, (
        "labworker doit être actif (après restart avec la nouvelle priorité)."
    )


def test_process_nice_is_10(host):
    """Le processus du service doit tourner à nice 10 (priorité abaissée)."""
    pid = host.check_output("systemctl show -p MainPID --value %s", SERVICE).strip()
    assert pid.isdigit() and pid != "0", (
        f"MainPID de labworker introuvable (vu : {pid!r}) — le service tourne-t-il ?"
    )
    ni = host.check_output("ps -o ni= -p %s", pid).strip()
    assert ni == "10", (
        f"Le processus de labworker doit tourner à nice 10 (vu : {ni!r}). "
        "Ajoute Nice=10 à l'unit puis daemon-reload + restart."
    )


def test_nice_in_unit_config(host):
    """La priorité doit être déclarée dans l'unit (persistance reboot)."""
    out = host.check_output(
        "grep -rhs -i 'Nice=' /etc/systemd/system/labworker.service "
        "/etc/systemd/system/labworker.service.d/ 2>/dev/null || true"
    )
    assert "10" in out.replace(" ", ""), (
        "Nice=10 doit figurer dans l'unit ou un drop-in "
        "(sinon la priorité serait perdue au redémarrage). Vu :\n"
        f"{out}"
    )
