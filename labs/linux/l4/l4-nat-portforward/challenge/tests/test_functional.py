"""Tests pytest+testinfra — l4-nat-portforward.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : routage IP (live + persistant), les règles NAT nftables
(DNAT + masquerade) et la persistance du ruleset (service + include RHEL).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_ip_forward_live(host):
    """Le routage IP doit être actif."""
    val = host.check_output("sysctl -n net.ipv4.ip_forward").strip()
    assert val == "1", (
        f"net.ipv4.ip_forward doit valoir 1 (vu : {val!r}) — préalable au NAT."
    )


def test_ip_forward_persistent(host):
    """Le routage IP doit être déclaré dans /etc/sysctl.d (persistance reboot)."""
    out = host.check_output(
        "grep -rhs ip_forward /etc/sysctl.d/ /etc/sysctl.conf 2>/dev/null || true"
    )
    assert "net.ipv4.ip_forward" in out and "1" in out, (
        "net.ipv4.ip_forward=1 doit être dans /etc/sysctl.d/ (sinon perdu au "
        f"reboot). Vu :\n{out}"
    )


def test_dnat_rule(host):
    """Le ruleset doit contenir la redirection de port (DNAT)."""
    ruleset = host.check_output("nft list ruleset")
    assert "dport 8080 dnat to 192.0.2.20:80" in ruleset, (
        "La règle prerouting 'tcp dport 8080 dnat to 192.0.2.20:80' doit exister."
    )


def test_masquerade_rule(host):
    """Le ruleset doit contenir le masquerade (SNAT)."""
    ruleset = host.check_output("nft list ruleset")
    assert "192.0.2.20 masquerade" in ruleset, (
        "La règle postrouting '192.0.2.20 masquerade' doit exister."
    )


def test_ruleset_persistent(host):
    """Le ruleset doit persister : service nftables activé + include RHEL."""
    assert host.service("nftables").is_enabled, (
        "nftables.service doit être enabled (sinon les règles disparaissent au "
        "reboot). systemctl enable nftables"
    )
    conf = host.file("/etc/sysconfig/nftables.conf")
    assert conf.exists and "lab-nat.nft" in conf.content_string, (
        "Le ruleset de lab doit être inclus dans /etc/sysconfig/nftables.conf "
        "(persistance)."
    )
