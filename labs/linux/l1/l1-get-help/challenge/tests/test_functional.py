"""test_functional.py — l1-get-help (refonte : trouver via l'aide, puis FAIRE)

Avant : l'apprenant écrivait le nom d'une commande trouvée — jamais exécutée.
Après : il utilise `man`/`--help`/`apropos` pour trouver le bon outil, puis
l'UTILISE pour produire un résultat. Le test compare les artefacts produits au
contenu réel de la source : trouver le bon outil ET s'en servir correctement.

Point de départ : `donnees.txt` (5 lignes de log, dont 2 « ERROR »), copié par
`dsoxlab run`. Attendu, produit par l'apprenant dans challenge/work/ :
  - fin.txt      : les 3 DERNIÈRES lignes de donnees.txt   (tail)
  - compte.txt   : le NOMBRE de lignes de donnees.txt       (wc -l)
  - erreurs.txt  : uniquement les lignes contenant ERROR    (grep)
"""
from __future__ import annotations

import pathlib
import re

WORK = pathlib.Path(".")
SOURCE = WORK / "donnees.txt"


def _source_lines() -> list[str]:
    assert SOURCE.exists(), (
        "donnees.txt introuvable — lance : dsoxlab run l1-get-help"
    )
    return [ln for ln in SOURCE.read_text(encoding="utf-8").splitlines() if ln]


# ── Point de départ ───────────────────────────────────────────────────────────

def test_source_present() -> None:
    assert SOURCE.exists(), (
        "donnees.txt introuvable — lance : dsoxlab run l1-get-help"
    )


# ── tail : les 3 dernières lignes ─────────────────────────────────────────────

def test_fin_is_last_three_lines() -> None:
    """fin.txt doit contenir exactement les 3 dernières lignes de donnees.txt."""
    fin = WORK / "fin.txt"
    assert fin.exists(), (
        "fin.txt manquant. Trouve la commande des dernières lignes (apropos last / "
        "man tail), puis : tail -n 3 donnees.txt > fin.txt"
    )
    got = [ln for ln in fin.read_text(encoding="utf-8").splitlines() if ln]
    expected = _source_lines()[-3:]
    assert got == expected, (
        f"fin.txt ne contient pas les 3 dernières lignes attendues.\n"
        f"Attendu : {expected}\nObtenu : {got}\n"
        "Utilise : tail -n 3 donnees.txt > fin.txt"
    )


# ── wc : le nombre de lignes ──────────────────────────────────────────────────

def test_compte_is_line_count() -> None:
    """compte.txt doit contenir le nombre de lignes de donnees.txt."""
    compte = WORK / "compte.txt"
    assert compte.exists(), (
        "compte.txt manquant. Trouve la commande qui compte les lignes "
        "(man wc), puis : wc -l donnees.txt > compte.txt"
    )
    m = re.search(r"\d+", compte.read_text(encoding="utf-8"))
    assert m, "compte.txt ne contient aucun nombre. Utilise : wc -l donnees.txt > compte.txt"
    assert int(m.group()) == len(_source_lines()), (
        f"compte.txt indique {m.group()} mais donnees.txt a "
        f"{len(_source_lines())} lignes. Utilise : wc -l donnees.txt > compte.txt"
    )


# ── grep : uniquement les lignes ERROR ────────────────────────────────────────

def test_erreurs_are_error_lines() -> None:
    """erreurs.txt doit contenir uniquement les lignes ERROR de donnees.txt."""
    err = WORK / "erreurs.txt"
    assert err.exists(), (
        "erreurs.txt manquant. Trouve la commande qui filtre un motif "
        "(apropos pattern / man grep), puis : grep ERROR donnees.txt > erreurs.txt"
    )
    got = [ln for ln in err.read_text(encoding="utf-8").splitlines() if ln]
    expected = [ln for ln in _source_lines() if "ERROR" in ln]
    assert got == expected, (
        f"erreurs.txt ne correspond pas aux lignes ERROR attendues.\n"
        f"Attendu : {expected}\nObtenu : {got}\n"
        "Utilise : grep ERROR donnees.txt > erreurs.txt"
    )
