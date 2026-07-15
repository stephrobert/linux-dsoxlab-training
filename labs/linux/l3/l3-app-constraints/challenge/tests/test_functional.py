"""Tests pytest+testinfra — l3-app-constraints.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la limite EFFECTIVE de fichiers ouverts d'appuser dans une
vraie session (su - appuser), via pam_limits — pas seulement le fichier de conf.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_limits_file_present(host):
    """Un drop-in limits.d doit définir nofile pour appuser."""
    out = host.check_output(
        "grep -rhs 'appuser' /etc/security/limits.conf "
        "/etc/security/limits.d/ 2>/dev/null || true"
    )
    assert "nofile" in out, (
        "Il faut une entrée nofile pour appuser dans /etc/security/limits.d/ "
        f"(ou limits.conf). Vu :\n{out}"
    )


def test_effective_soft_nofile(host):
    """La limite SOUPLE effective d'appuser doit être 4096 (via pam_limits)."""
    val = host.check_output("su - appuser -c 'ulimit -Sn'").strip()
    assert val == "4096", (
        f"ulimit -Sn d'appuser doit valoir 4096 (vu : {val!r}). "
        "appuser soft nofile 4096"
    )


def test_effective_hard_nofile(host):
    """La limite DURE effective d'appuser doit être 8192."""
    val = host.check_output("su - appuser -c 'ulimit -Hn'").strip()
    assert val == "8192", (
        f"ulimit -Hn d'appuser doit valoir 8192 (vu : {val!r}). "
        "appuser hard nofile 8192"
    )
