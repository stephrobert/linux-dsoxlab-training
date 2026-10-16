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

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"
REPO_FILE = "/etc/yum.repos.d/labrepo.repo"
REPO_ID = "labrepo"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module")
def repo_cfg(host) -> configparser.ConfigParser:
    f = host.file(REPO_FILE)
    assert f.exists, message(
        en=f"{REPO_FILE} is missing. Create the repository definition under /etc/yum.repos.d/.",
        fr=f"{REPO_FILE} manquant. Crée la définition du dépôt sous /etc/yum.repos.d/.",
    )
    cfg = configparser.ConfigParser()
    cfg.read_string(f.content_string)
    return cfg


def test_repo_section_present(repo_cfg):
    assert REPO_ID in repo_cfg.sections(), message(
        en=f"The file must contain a [{REPO_ID}] section. "
        f"Sections seen: {repo_cfg.sections()}",
        fr=f"Le fichier doit contenir une section [{REPO_ID}]. "
        f"Sections vues : {repo_cfg.sections()}",
    )


def test_repo_has_baseurl(repo_cfg):
    base = repo_cfg[REPO_ID].get("baseurl", "").strip()
    assert base.startswith("http"), message(
        en=f"[{REPO_ID}] must have a valid http(s) baseurl (seen: {base!r}).",
        fr=f"[{REPO_ID}] doit avoir une baseurl http(s) valide (vu : {base!r}).",
    )


def test_repo_enabled(repo_cfg):
    assert repo_cfg[REPO_ID].get("enabled", "").strip() == "1", message(
        en=f"[{REPO_ID}] must be enabled=1.",
        fr=f"[{REPO_ID}] doit être enabled=1.",
    )


def test_repo_gpgcheck(repo_cfg):
    assert repo_cfg[REPO_ID].get("gpgcheck", "").strip() == "1", message(
        en=f"[{REPO_ID}] must have gpgcheck=1 (security: verify the signatures).",
        fr=f"[{REPO_ID}] doit avoir gpgcheck=1 (sécurité : vérifier les signatures).",
    )


def test_dnf_sees_repo(host):
    """dnf doit reconnaître l'id du dépôt dans sa liste."""
    out = host.check_output("dnf repolist --all 2>/dev/null")
    assert REPO_ID in out, message(
        en=f"dnf does not see the '{REPO_ID}' repository (dnf repolist --all). "
        "Check the syntax of the .repo file.",
        fr=f"dnf ne voit pas le dépôt '{REPO_ID}' (dnf repolist --all). "
        "Vérifie la syntaxe du fichier .repo.",
    )
