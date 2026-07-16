"""Tests pytest+testinfra — lfcs-storage-quotas.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le disque est monté en XFS, les quotas utilisateur sont
réellement ACTIFS (accounting + enforcement dans le noyau), l'entrée fstab rend
le tout persistant (le piège : un montage manuel perd les quotas au reboot), et
la limite de devops est effectivement appliquée.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "ubuntu-lfcs-1.lab"
MOUNT = "/srv/data"
DEVICE = "/dev/vdb"
QUOTA_USER = "devops"
# xfs_quota rend les limites en blocs de 1 Ko : 40M -> 40960, 50M -> 51200.
BSOFT_KB = 40960
BHARD_KB = 51200


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _fstab_line(host) -> str | None:
    """Retourne la ligne fstab qui monte MOUNT, sinon None."""
    fstab = host.file("/etc/fstab").content_string
    for line in fstab.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2 and fields[1] == MOUNT:
            return stripped
    return None


def test_mounted_from_dedicated_disk(host):
    """/srv/data doit être monté depuis /dev/vdb, en XFS."""
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} n'est pas monté. Formate {DEVICE} en XFS puis monte-le."
    )
    source, fstype = host.check_output(
        "findmnt -no SOURCE,FSTYPE %s", MOUNT
    ).split()
    assert source == DEVICE, (
        f"{MOUNT} doit être monté depuis {DEVICE} (vu : {source!r})."
    )
    assert fstype == "xfs", (
        f"{MOUNT} doit être un système de fichiers XFS (vu : {fstype!r})."
    )


def test_user_quota_enforced(host):
    """Les quotas utilisateur doivent être actifs ET appliqués sur le montage."""
    state = host.check_output('xfs_quota -x -c "state -u" %s', MOUNT)
    assert "Accounting: ON" in state, (
        "La comptabilité des quotas utilisateur est OFF : le montage n'a pas "
        "été fait avec l'option uquota. Vu :\n" + state
    )
    assert "Enforcement: ON" in state, (
        "L'application des quotas utilisateur est OFF : la limite ne serait "
        "jamais imposée. Vu :\n" + state
    )


def test_fstab_persistent_with_quota_option(host):
    """L'entrée fstab doit rendre le montage ET les quotas persistants."""
    line = _fstab_line(host)
    assert line is not None, (
        f"Aucune entrée fstab pour {MOUNT} : le montage disparaîtrait au "
        f"reboot. Ajoute : {DEVICE} {MOUNT} xfs defaults,uquota 0 0"
    )
    fields = line.split()
    assert len(fields) >= 4 and fields[2] == "xfs", (
        f"L'entrée fstab de {MOUNT} doit être de type xfs (vu : {line!r})."
    )
    opts = fields[3].split(",")
    assert any(o in ("uquota", "usrquota", "quota") for o in opts), (
        "L'entrée fstab doit porter l'option de quota utilisateur (uquota), "
        "sinon les quotas sont perdus au reboot — c'est LE piège. "
        f"Vu : {fields[3]!r}."
    )


def test_devops_block_limit_applied(host):
    """devops doit porter la limite de blocs demandée (40M souple / 50M dure)."""
    report = host.check_output('xfs_quota -x -c "report -u -N -b" %s', MOUNT)
    line = next(
        (ligne for ligne in report.splitlines() if ligne.split() and ligne.split()[0] == QUOTA_USER),
        None,
    )
    assert line is not None, (
        f"L'utilisateur {QUOTA_USER} n'apparaît pas dans le rapport de quotas. "
        f'Impose la limite : xfs_quota -x -c "limit bsoft=40m bhard=50m '
        f'{QUOTA_USER}" {MOUNT}. Vu :\n{report}'
    )
    fields = line.split()
    soft, hard = int(fields[2]), int(fields[3])
    assert soft == BSOFT_KB, (
        f"Le quota souple de {QUOTA_USER} doit être 40M ({BSOFT_KB} blocs de "
        f"1K), vu : {soft}."
    )
    assert hard == BHARD_KB, (
        f"Le quota dur de {QUOTA_USER} doit être 50M ({BHARD_KB} blocs de 1K), "
        f"vu : {hard}."
    )
