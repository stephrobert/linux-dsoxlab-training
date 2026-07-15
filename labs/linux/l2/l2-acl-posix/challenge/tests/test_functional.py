"""Tests pytest+testinfra — l2-acl-posix.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT des ACL réelles lues par getfacl : entrée utilisateur sur le
fichier, entrée groupe sur le répertoire, et ACL par défaut héritée.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
DIR = "/srv/projet"
FILE = "/srv/projet/report.txt"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _facl(host, path: str) -> list[str]:
    # -p : ne pas retirer le / initial ; sortie stable ligne par ligne.
    out = host.check_output("getfacl -p %s 2>/dev/null", path)
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def test_user_acl_on_file(host):
    """carol doit avoir rw via ACL sur report.txt."""
    entries = _facl(host, FILE)
    assert "user:carol:rw-" in entries, (
        "Il manque l'ACL utilisateur carol:rw- sur report.txt. "
        f"setfacl -m u:carol:rw {FILE}\ngetfacl : {entries}"
    )


def test_group_acl_on_dir(host):
    """auditors doit avoir r-x via ACL sur le répertoire."""
    entries = _facl(host, DIR)
    assert "group:auditors:r-x" in entries, (
        "Il manque l'ACL groupe auditors:r-x sur le répertoire. "
        f"setfacl -m g:auditors:rx {DIR}\ngetfacl : {entries}"
    )


def test_default_acl_on_dir(host):
    """Une ACL PAR DÉFAUT doit donner r au groupe auditors aux futurs fichiers."""
    entries = _facl(host, DIR)
    has_default = any(
        e.startswith("default:group:auditors:") and "r" in e.split(":")[-1]
        for e in entries
    )
    assert has_default, (
        "Il manque l'ACL par défaut default:group:auditors:r-- sur le "
        f"répertoire (héritage). setfacl -m d:g:auditors:r {DIR}\ngetfacl : {entries}"
    )
