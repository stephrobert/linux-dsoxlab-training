"""Tests pytest+testinfra — l3-sysctl-persist.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : les valeurs sysctl ACTIVES (noyau) ET leur présence dans
/etc/sysctl.d (persistance après reboot).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
PARAMS = {
    "net.ipv4.ip_forward": "0",
    "net.ipv4.conf.all.accept_redirects": "0",
}


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.mark.parametrize("param,expected", PARAMS.items())
def test_live_value(host, param, expected):
    """La valeur active du paramètre noyau doit être durcie."""
    val = host.check_output("sysctl -n %s", param).strip()
    assert val == expected, (
        f"{param} doit valoir {expected} en live (vu : {val!r}). "
        "Après édition du drop-in : sudo sysctl --system"
    )


def test_persisted_in_sysctl_d(host):
    """Les réglages doivent être dans /etc/sysctl.d (persistance reboot)."""
    out = host.check_output(
        "grep -rhs -E 'ip_forward|accept_redirects' /etc/sysctl.d/ "
        "/etc/sysctl.conf 2>/dev/null || true"
    )
    for param in PARAMS:
        assert param in out, (
            f"{param} doit être déclaré dans /etc/sysctl.d/ (sinon perdu au "
            f"reboot). Contenu vu :\n{out}"
        )
