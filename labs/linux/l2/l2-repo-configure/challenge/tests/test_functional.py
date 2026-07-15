"""Tests pytest+testinfra — l2-repo-configure.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le fichier .repo réel (parsé en INI) déclare un dépôt activé
et vérifié GPG avec une baseurl, ET dnf reconnaît l'id du dépôt.
"""
from __future__ import annotations

import configparser

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
REPO_FILE = "/etc/yum.repos.d/labrepo.repo"
REPO_ID = "labrepo"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module")
def repo_cfg(host) -> configparser.ConfigParser:
    f = host.file(REPO_FILE)
    assert f.exists, (
        f"{REPO_FILE} manquant. Crée la définition du dépôt sous /etc/yum.repos.d/."
    )
    cfg = configparser.ConfigParser()
    cfg.read_string(f.content_string)
    return cfg


def test_repo_section_present(repo_cfg):
    assert REPO_ID in repo_cfg.sections(), (
        f"Le fichier doit contenir une section [{REPO_ID}]. "
        f"Sections vues : {repo_cfg.sections()}"
    )


def test_repo_has_baseurl(repo_cfg):
    base = repo_cfg[REPO_ID].get("baseurl", "").strip()
    assert base.startswith("http"), (
        f"[{REPO_ID}] doit avoir une baseurl http(s) valide (vu : {base!r})."
    )


def test_repo_enabled(repo_cfg):
    assert repo_cfg[REPO_ID].get("enabled", "").strip() == "1", (
        f"[{REPO_ID}] doit être enabled=1."
    )


def test_repo_gpgcheck(repo_cfg):
    assert repo_cfg[REPO_ID].get("gpgcheck", "").strip() == "1", (
        f"[{REPO_ID}] doit avoir gpgcheck=1 (sécurité : vérifier les signatures)."
    )


def test_dnf_sees_repo(host):
    """dnf doit reconnaître l'id du dépôt dans sa liste."""
    out = host.check_output("dnf repolist --all 2>/dev/null")
    assert REPO_ID in out, (
        f"dnf ne voit pas le dépôt '{REPO_ID}' (dnf repolist --all). "
        "Vérifie la syntaxe du fichier .repo."
    )
