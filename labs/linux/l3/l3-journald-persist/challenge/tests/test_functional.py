"""Tests pytest+testinfra — l3-journald-persist.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : /var/log/journal existe, la config déclare Storage=persistent,
et journald a réellement écrit un fichier journal persistant (pas juste la
config).
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_journal_dir_exists(host):
    """/var/log/journal doit exister (répertoire du stockage persistant)."""
    assert host.file("/var/log/journal").is_directory, (
        "/var/log/journal doit exister : sudo mkdir -p /var/log/journal"
    )


def test_storage_persistent_config(host):
    """La config journald doit déclarer Storage=persistent."""
    out = host.check_output(
        "grep -rhs '^[[:space:]]*Storage=' "
        "/etc/systemd/journald.conf /etc/systemd/journald.conf.d/ 2>/dev/null || true"
    )
    values = [line.split("=", 1)[1].strip() for line in out.splitlines() if "=" in line]
    assert "persistent" in values, (
        "La config doit contenir Storage=persistent (journald.conf ou un "
        f"drop-in journald.conf.d/). Valeurs vues : {values}"
    )


def test_persistent_journal_written(host):
    """journald doit avoir réellement écrit un journal sous /var/log/journal."""
    count = host.check_output(
        "find /var/log/journal -name '*.journal' 2>/dev/null | wc -l"
    )
    assert count.strip().isdigit() and int(count) >= 1, (
        "Aucun fichier .journal sous /var/log/journal : après Storage=persistent, "
        "redémarre systemd-journald (et journalctl --flush) pour qu'il écrive sur disque."
    )
