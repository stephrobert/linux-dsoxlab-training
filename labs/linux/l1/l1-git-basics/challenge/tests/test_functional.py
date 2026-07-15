"""test_functional.py — l1-git-basics

Prouve l'ÉTAT du dépôt Git réel : on interroge le dépôt avec git lui-même
(log, ls-files, branch, status). Taper les commandes sans obtenir l'état
attendu (rien commité, aucune branche) échoue.

Point de départ : un répertoire de travail vide. L'apprenant crée le dépôt
`monprojet/`.
"""
from __future__ import annotations

import pathlib
import subprocess

WORK = pathlib.Path(".")
REPO = WORK / "monprojet"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True,
        text=True,
        timeout=15,
    )


def test_repo_initialized() -> None:
    assert (REPO / ".git").is_dir(), (
        "Le dépôt monprojet/ n'existe pas. Crée-le : mkdir monprojet && "
        "cd monprojet && git init"
    )


def test_at_least_two_commits() -> None:
    res = _git("log", "--oneline")
    assert res.returncode == 0, (
        "git log échoue : le dépôt n'a aucun commit. Fais au moins deux commits."
    )
    commits = [ln for ln in res.stdout.splitlines() if ln.strip()]
    assert len(commits) >= 2, (
        f"Le dépôt doit avoir au moins 2 commits, trouvé {len(commits)}."
    )


def test_files_are_tracked() -> None:
    tracked = set(_git("ls-files").stdout.split())
    for expected in ("README.md", "app.sh"):
        assert expected in tracked, (
            f"{expected} doit être suivi par Git (git add + git commit). "
            f"Fichiers suivis : {sorted(tracked)}"
        )


def test_feature_branch_exists() -> None:
    branches = _git("branch", "--format=%(refname:short)").stdout.split()
    assert "feature" in branches, (
        f"La branche 'feature' doit exister (git branch feature ou "
        f"git switch -c feature). Branches : {branches}"
    )


def test_working_tree_clean() -> None:
    """Tout est commité : git status ne signale rien en attente."""
    porcelain = _git("status", "--porcelain").stdout.strip()
    assert porcelain == "", (
        "L'arbre de travail doit être propre (tout commité). "
        f"En attente :\n{porcelain}"
    )
