"""Tests pytest+testinfra — l3-boot-target.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la cible systemd par défaut réelle (systemctl get-default),
qui pilote le prochain démarrage.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_default_target_is_multi_user(host):
    """La cible par défaut doit être multi-user.target."""
    default = host.check_output("systemctl get-default")
    assert default.strip() == "multi-user.target", (
        f"La cible par défaut doit être multi-user.target (vue : {default!r}). "
        "systemctl set-default multi-user.target"
    )
