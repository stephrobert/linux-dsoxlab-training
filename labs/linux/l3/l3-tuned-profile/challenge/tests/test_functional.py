"""Tests pytest+testinfra — l3-tuned-profile.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le profil tuned RÉELLEMENT actif (tuned-adm active) et sa
persistance (fichier active_profile).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
PROFILE = "throughput-performance"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_tuned_running(host):
    """Le service tuned doit tourner."""
    assert host.service("tuned").is_running, (
        "tuned doit être actif : systemctl enable --now tuned"
    )


def test_active_profile(host):
    """Le profil actif doit être throughput-performance."""
    out = host.check_output("tuned-adm active")
    assert PROFILE in out, (
        f"Le profil tuned actif doit être {PROFILE} (vu : {out!r}). "
        f"tuned-adm profile {PROFILE}"
    )


def test_profile_persisted(host):
    """Le profil doit être enregistré (persistance après reboot)."""
    content = host.file("/etc/tuned/active_profile").content_string.strip()
    assert content == PROFILE, (
        f"/etc/tuned/active_profile doit contenir {PROFILE} (vu : {content!r}) "
        "pour survivre au reboot."
    )
