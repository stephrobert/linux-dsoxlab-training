"""Tests pytest+testinfra — l2-password-policy.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : l'expiration réelle de bob (chage -l), le défaut système
(login.defs) et la longueur mini (pwquality) — pas la commande tapée.
"""
from __future__ import annotations

import re

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module")
def chage(host) -> str:
    # LC_ALL=C : les libellés de chage -l sont localisés, on force l'anglais.
    return host.check_output("LC_ALL=C chage -l bob")


def _field(text: str, label: str) -> str:
    m = re.search(rf"{label}\s*:\s*(.+)", text)
    return m.group(1).strip() if m else ""


def test_max_age_60(chage):
    val = _field(chage, "Maximum number of days between password change")
    assert val == "60", f"L'âge max du mot de passe de bob doit être 60 (vu : {val!r}). chage -M 60 bob"


def test_min_age_7(chage):
    val = _field(chage, "Minimum number of days between password change")
    assert val == "7", f"L'âge min doit être 7 (vu : {val!r}). chage -m 7 bob"


def test_warn_7(chage):
    val = _field(chage, "Number of days of warning before password expires")
    assert val == "7", f"L'avertissement doit être 7 jours (vu : {val!r}). chage -W 7 bob"


def test_login_defs_max_days(host):
    """Le défaut système PASS_MAX_DAYS doit être 60."""
    content = host.file("/etc/login.defs").content_string
    m = re.search(r"^\s*PASS_MAX_DAYS\s+(\d+)", content, re.M)
    assert m and m.group(1) == "60", (
        "PASS_MAX_DAYS doit valoir 60 dans /etc/login.defs "
        f"(vu : {m.group(1) if m else 'absent'})."
    )


def test_pwquality_minlen_12(host):
    """La longueur minimale doit être 12 dans pwquality.conf."""
    content = host.file("/etc/security/pwquality.conf").content_string
    m = re.search(r"^\s*minlen\s*=\s*(\d+)", content, re.M)
    assert m and int(m.group(1)) >= 12, (
        "minlen doit être >= 12 dans /etc/security/pwquality.conf "
        f"(vu : {m.group(1) if m else 'absent/commenté'})."
    )
