"""Tests pytest+testinfra — l2-disk-space-troubleshoot.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : /srv/data toujours monté, occupation redescendue sous 50 %,
et la donnée légitime (app.log) conservée — l'apprenant a récupéré de l'espace
sans tout détruire.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
MOUNT = "/srv/data"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_filesystem_still_mounted(host):
    """/srv/data doit rester monté (on ne résout pas en démontant/effaçant tout)."""
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} doit rester monté. Le but est de libérer de l'espace, "
        "pas de démonter le filesystem."
    )


def test_usage_below_50_percent(host):
    """L'occupation de /srv/data doit être redescendue sous 50 %."""
    pct_raw = host.check_output(
        "df --output=pcent %s | tail -1 | tr -dc '0-9'", MOUNT
    )
    pct = int(pct_raw) if pct_raw.isdigit() else 100
    assert pct < 50, (
        f"{MOUNT} est encore occupé à {pct}%. Trouve le gros consommateur "
        "(du -h --max-depth=1 /srv/data) et supprime-le pour repasser sous 50 %."
    )


def test_legit_data_kept(host):
    """Le fichier légitime app.log doit être conservé."""
    f = host.file(f"{MOUNT}/app.log")
    assert f.exists, (
        f"{MOUNT}/app.log a disparu : ne supprime que le superflu (le cache), "
        "pas les données légitimes."
    )
