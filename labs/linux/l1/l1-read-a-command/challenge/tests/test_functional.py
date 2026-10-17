"""test_functional.py — l1-read-a-command (refonte : lire puis PRODUIRE)

Avant : l'apprenant décomposait des commandes en texte (COMMAND/OPTIONS/
ARGUMENTS) — jamais exécuté. Après : il doit comprendre `cp`, `tar` et `cat`
assez bien pour les UTILISER et produire les bons artefacts. Le test vérifie les
fichiers réellement créés dans le workdir, pas la description d'une commande.

Point de départ : `source.txt` (5 lignes), copié par `dsoxlab run`.
Attendu, produit par l'apprenant dans challenge/work/ :
  - copie.txt        : copie exacte de source.txt        (cp)
  - archive.tar.gz   : archive gzip contenant source.txt (tar -czf)
  - numerote.txt     : source.txt avec numéros de ligne  (cat -n)
"""
from __future__ import annotations

import pathlib
import re
import tarfile

from conftest import message

WORK = pathlib.Path(".")
SOURCE = WORK / "source.txt"


def _source_text() -> str:
    assert SOURCE.exists(), message(
        en="source.txt cannot be found. Run: dsoxlab run l1-read-a-command",
        fr="source.txt introuvable — lance : dsoxlab run l1-read-a-command",
    )
    return SOURCE.read_text(encoding="utf-8")


# ── Point de départ ───────────────────────────────────────────────────────────

# ── cp : produire une copie exacte ────────────────────────────────────────────

def test_copie_is_exact_copy() -> None:
    """copie.txt doit être une copie exacte de source.txt (via cp)."""
    copie = WORK / "copie.txt"
    assert copie.exists(), message(
        en="copie.txt is missing. Copy source.txt: cp source.txt copie.txt",
        fr="copie.txt manquant. Copie source.txt : cp source.txt copie.txt",
    )
    assert copie.read_text(encoding="utf-8") == _source_text(), message(
        en="copie.txt differs from source.txt. Use `cp source.txt copie.txt` "
        "(no manual editing).",
        fr="copie.txt diffère de source.txt — utilise `cp source.txt copie.txt` "
        "(pas d'édition manuelle).",
    )


# ── tar : produire une archive gzip ───────────────────────────────────────────

def test_archive_contains_source() -> None:
    """archive.tar.gz doit être une archive gzip valide contenant source.txt."""
    arch = WORK / "archive.tar.gz"
    assert arch.exists(), message(
        en="archive.tar.gz is missing. Create it: tar -czf archive.tar.gz source.txt",
        fr="archive.tar.gz manquant. Crée-la : tar -czf archive.tar.gz source.txt",
    )
    assert tarfile.is_tarfile(arch), message(
        en="archive.tar.gz is not a valid tar archive. "
        "Use: tar -czf archive.tar.gz source.txt",
        fr="archive.tar.gz n'est pas une archive tar valide. "
        "Utilise : tar -czf archive.tar.gz source.txt",
    )
    with tarfile.open(arch) as tf:
        members = [pathlib.Path(m).name for m in tf.getnames()]
    assert "source.txt" in members, message(
        en=f"archive.tar.gz does not contain source.txt (seen: {members}). "
        "Archive source.txt itself.",
        fr=f"archive.tar.gz ne contient pas source.txt (vu : {members}). "
        "Archive bien source.txt.",
    )


# ── cat -n : produire un fichier numéroté ─────────────────────────────────────

def test_numerote_has_line_numbers() -> None:
    """numerote.txt doit être source.txt numéroté (via cat -n)."""
    num = WORK / "numerote.txt"
    assert num.exists(), message(
        en="numerote.txt is missing. Number source.txt: cat -n source.txt > numerote.txt",
        fr="numerote.txt manquant. Numérote source.txt : cat -n source.txt > numerote.txt",
    )
    content = num.read_text(encoding="utf-8")
    src_lines = [ln for ln in _source_text().splitlines() if ln]
    # Chaque ligne source doit apparaître préfixée d'un numéro croissant.
    for i, line in enumerate(src_lines, start=1):
        assert re.search(rf"^\s*{i}\s+{re.escape(line)}\s*$", content, re.MULTILINE), message(
            en=f"Line {i} ('{line}') not found numbered in numerote.txt. "
            "Use: cat -n source.txt > numerote.txt",
            fr=f"Ligne {i} ('{line}') non trouvée numérotée dans numerote.txt. "
            "Utilise : cat -n source.txt > numerote.txt",
        )
