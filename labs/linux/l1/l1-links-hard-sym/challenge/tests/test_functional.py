"""test_functional.py — l1-links-hard-sym

Prouve l'ÉTAT du système de fichiers : inode partagé (lien physique), compteur
de liens, et cible réelle du lien symbolique (readlink). Impossible à tromper :
un simple `cp` échoue le test d'inode, un fichier régulier échoue islink().

Point de départ : `original.txt`, copié par `dsoxlab run`.
"""
from __future__ import annotations

import os
import pathlib

WORK = pathlib.Path(".")
SOURCE = WORK / "original.txt"


def test_source_present() -> None:
    assert SOURCE.exists(), (
        "original.txt introuvable — lance : dsoxlab run l1-links-hard-sym"
    )


def test_hard_link_shares_inode() -> None:
    """copie-dure.txt = lien physique : MÊME inode que original.txt (pas une copie)."""
    hard = WORK / "copie-dure.txt"
    assert hard.exists(), (
        "copie-dure.txt manquant. Crée un lien physique : ln original.txt copie-dure.txt"
    )
    assert not hard.is_symlink(), (
        "copie-dure.txt doit être un lien PHYSIQUE (ln sans -s), pas symbolique."
    )
    assert hard.stat().st_ino == SOURCE.stat().st_ino, (
        "copie-dure.txt doit partager l'inode de original.txt. "
        "Un `cp` crée un nouvel inode — utilise `ln` (sans -s)."
    )


def test_original_link_count_is_two() -> None:
    """Le lien physique fait passer le compteur de liens de original.txt à 2."""
    n = SOURCE.stat().st_nlink
    assert n == 2, (
        f"original.txt devrait avoir 2 liens physiques (lui-même + copie-dure.txt), "
        f"trouvé {n}. Vérifie que copie-dure.txt est bien un lien physique (ln, pas cp)."
    )


def test_symlink_to_file() -> None:
    """raccourci.txt = lien symbolique vers original.txt (pointe par chemin)."""
    link = WORK / "raccourci.txt"
    assert link.is_symlink(), (
        "raccourci.txt doit être un lien symbolique : ln -s original.txt raccourci.txt"
    )
    target = os.readlink(link)
    assert pathlib.PurePath(target).name == "original.txt", (
        f"raccourci.txt doit pointer vers original.txt, pointe vers {target!r}."
    )
    assert link.read_text(encoding="utf-8") == SOURCE.read_text(encoding="utf-8"), (
        "raccourci.txt doit donner accès au contenu de original.txt (lien valide)."
    )


def test_symlink_to_directory() -> None:
    """lien-data = lien symbolique vers un répertoire data/."""
    data = WORK / "data"
    assert data.is_dir() and not data.is_symlink(), (
        "Le répertoire data/ manque. Crée-le : mkdir data"
    )
    link = WORK / "lien-data"
    assert link.is_symlink(), (
        "lien-data doit être un lien symbolique vers data/ : ln -s data lien-data"
    )
    assert link.resolve() == data.resolve(), (
        "lien-data doit résoudre vers le répertoire data/."
    )
