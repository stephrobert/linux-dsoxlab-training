"""test_functional.py — l1-find-files

Prouve l'ÉTAT (les fichiers réellement produits par find), pas les commandes
tapées. Chaque attendu est recalculé depuis l'arbre extrait `projet/`, donc le
test est auto-cohérent (aucune valeur codée en dur, robuste au umask).

Point de départ : `projet.tar.gz` (copié par `dsoxlab run`), que l'apprenant
extrait avec `tar xpzf`.
"""
from __future__ import annotations

import os
import pathlib

from conftest import message

WORK = pathlib.Path(".")
TREE = WORK / "projet"


def _norm(p: str) -> str:
    return os.path.normpath(p.strip())


def _tree_files() -> list[str]:
    out = []
    for root, _dirs, files in os.walk(TREE):
        for f in files:
            out.append(os.path.join(root, f))
    return out


def _read_set(name: str) -> set[str]:
    f = WORK / name
    assert f.exists(), message(
        en=f"{name} is missing. Produce it with find (see the mission).",
        fr=f"{name} manquant — produis-le avec find (voir la mission).",
    )
    return {_norm(ln) for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()}


def test_archive_extracted() -> None:
    """L'archive doit être extraite (répertoire projet/)."""
    assert TREE.is_dir(), message(
        en="Extract the archive first, preserving the modes: "
        "tar xpzf projet.tar.gz",
        fr="Extrais d'abord l'archive en préservant les modes : "
        "tar xpzf projet.tar.gz",
    )


def test_logs() -> None:
    """logs.txt = les chemins des fichiers *.log sous projet/."""
    got = _read_set("logs.txt")
    expected = {_norm(p) for p in _tree_files() if p.endswith(".log")}
    assert got == expected, message(
        en=f"logs.txt must list the *.log files of projet/.\n"
        f"Expected: {sorted(expected)}\nGot: {sorted(got)}\n"
        "Hint: find projet -name '*.log'",
        fr=f"logs.txt doit lister les *.log de projet/.\n"
        f"Attendu : {sorted(expected)}\nObtenu : {sorted(got)}\n"
        "Indice : find projet -name '*.log'",
    )


def test_gros() -> None:
    """gros.txt = les fichiers réguliers de plus de 1000 octets."""
    got = _read_set("gros.txt")
    expected = {
        _norm(p) for p in _tree_files() if os.path.getsize(p) > 1000
    }
    assert got == expected, message(
        en=f"gros.txt must list the files larger than 1000 bytes.\n"
        f"Expected: {sorted(expected)}\nGot: {sorted(got)}\n"
        "Hint: find projet -type f -size +1000c",
        fr=f"gros.txt doit lister les fichiers > 1000 octets.\n"
        f"Attendu : {sorted(expected)}\nObtenu : {sorted(got)}\n"
        "Indice : find projet -type f -size +1000c",
    )


def test_prives() -> None:
    """prives.txt = les fichiers réguliers en mode exactement 600."""
    got = _read_set("prives.txt")
    expected = {
        _norm(p) for p in _tree_files()
        if (os.stat(p).st_mode & 0o777) == 0o600
    }
    assert got == expected, message(
        en=f"prives.txt must list the files in mode 600.\n"
        f"Expected: {sorted(expected)}\nGot: {sorted(got)}\n"
        "Hint: find projet -type f -perm 600 (and tar xpzf to keep the modes)",
        fr=f"prives.txt doit lister les fichiers en mode 600.\n"
        f"Attendu : {sorted(expected)}\nObtenu : {sorted(got)}\n"
        "Indice : find projet -type f -perm 600 (et tar xpzf pour garder les modes)",
    )
