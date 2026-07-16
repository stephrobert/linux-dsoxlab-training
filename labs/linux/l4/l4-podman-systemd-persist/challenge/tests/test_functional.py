"""Tests pytest+testinfra — l4-podman-systemd-persist.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : l'unité Quadlet sur disque avec [Install] (persistance boot),
le service généré actif, et le conteneur qui tourne.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_quadlet_unit_on_disk(host):
    """L'unité Quadlet doit exister avec [Install] WantedBy (persistance boot)."""
    unit = host.file("/etc/containers/systemd/weblab.container")
    assert unit.exists, (
        "/etc/containers/systemd/weblab.container doit exister (source Quadlet)."
    )
    content = unit.content_string
    assert "WantedBy" in content, (
        "L'unité doit avoir une section [Install] WantedBy= pour démarrer au boot."
    )


def test_service_active(host):
    """weblab.service (généré par Quadlet) doit être actif."""
    state = host.check_output("systemctl is-active weblab.service").strip()
    assert state == "active", (
        f"weblab.service doit être actif (vu : {state!r}). "
        "systemctl daemon-reload puis systemctl start weblab.service"
    )


def test_container_running(host):
    """Le conteneur weblab doit tourner."""
    state = host.check_output(
        "podman inspect -f '{{.State.Running}}' weblab"
    ).strip()
    assert state == "true", (
        f"Le conteneur weblab doit tourner (State.Running vu : {state!r})."
    )
