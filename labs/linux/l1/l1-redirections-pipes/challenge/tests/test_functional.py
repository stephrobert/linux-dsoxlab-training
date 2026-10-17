"""test_functional.py — l1-redirections-pipes

Prouve l'ÉTAT (les artefacts réellement produits par les redirections), pas les
commandes tapées : nombre de lignes redirigé, erreurs filtrées par pipe, sortie
d'erreur capturée avec 2>, et flux standard + erreur fusionnés avec 2>&1.

Point de départ : `journal.log` (5 lignes, dont 2 « ERROR »), copié par
`dsoxlab run`.
"""
from __future__ import annotations

import pathlib
import re

from conftest import message

WORK = pathlib.Path(".")
SOURCE = WORK / "journal.log"


def _lines() -> list[str]:
    assert SOURCE.exists(), message(
        en="journal.log cannot be found. Run: dsoxlab run l1-redirections-pipes",
        fr="journal.log introuvable — lance : dsoxlab run l1-redirections-pipes",
    )
    return [ln for ln in SOURCE.read_text(encoding="utf-8").splitlines() if ln]


def test_total_via_redirection() -> None:
    """total.txt = nombre de lignes de journal.log, via `>`."""
    f = WORK / "total.txt"
    assert f.exists(), message(
        en="total.txt is missing. Redirect the count: wc -l < journal.log > total.txt",
        fr="total.txt manquant. Redirige le compte : wc -l < journal.log > total.txt",
    )
    m = re.search(r"\d+", f.read_text(encoding="utf-8"))
    assert m and int(m.group()) == len(_lines()), message(
        en=f"total.txt must contain the number of lines ({len(_lines())}). "
        "Use: wc -l < journal.log > total.txt",
        fr=f"total.txt doit contenir le nombre de lignes ({len(_lines())}). "
        "Utilise : wc -l < journal.log > total.txt",
    )


def test_erreurs_via_pipe() -> None:
    """erreurs.txt = uniquement les lignes ERROR (grep + redirection)."""
    f = WORK / "erreurs.txt"
    assert f.exists(), message(
        en="erreurs.txt is missing. Filter: grep ERROR journal.log > erreurs.txt",
        fr="erreurs.txt manquant. Filtre : grep ERROR journal.log > erreurs.txt",
    )
    got = [ln for ln in f.read_text(encoding="utf-8").splitlines() if ln]
    expected = [ln for ln in _lines() if "ERROR" in ln]
    assert got == expected, message(
        en=f"erreurs.txt must contain the ERROR lines.\n"
        f"Expected: {expected}\nGot: {got}",
        fr=f"erreurs.txt doit contenir les lignes ERROR.\n"
        f"Attendu : {expected}\nObtenu : {got}",
    )


def test_stderr_captured() -> None:
    """stderr.txt = la SORTIE D'ERREUR d'une commande qui échoue, via `2>`."""
    f = WORK / "stderr.txt"
    assert f.exists(), message(
        en="stderr.txt is missing. Capture the error: cat inexistant.txt 2> stderr.txt",
        fr="stderr.txt manquant. Capture l'erreur : cat inexistant.txt 2> stderr.txt",
    )
    content = f.read_text(encoding="utf-8").strip()
    assert content, message(
        en="stderr.txt is empty: redirect the error output properly with 2>.",
        fr="stderr.txt est vide : redirige bien la sortie d'erreur avec 2>.",
    )
    assert "inexistant" in content, message(
        en="stderr.txt must contain the error message for a missing file "
        "(cat inexistant.txt 2> stderr.txt).",
        fr="stderr.txt doit contenir le message d'erreur d'un fichier absent "
        "(cat inexistant.txt 2> stderr.txt).",
    )


def test_merged_stdout_stderr() -> None:
    """tout.txt = sortie standard ET erreur fusionnées, via `2>&1` (ou `&>`)."""
    f = WORK / "tout.txt"
    assert f.exists(), message(
        en="tout.txt is missing. Merge: ls journal.log inexistant.txt > tout.txt 2>&1",
        fr="tout.txt manquant. Fusionne : ls journal.log inexistant.txt > tout.txt 2>&1",
    )
    content = f.read_text(encoding="utf-8")
    assert "journal.log" in content, message(
        en="tout.txt must contain standard output (journal.log).",
        fr="tout.txt doit contenir la sortie standard (journal.log).",
    )
    assert "inexistant" in content, message(
        en="tout.txt must ALSO contain the error: redirect stdout AND stderr "
        "(2>&1 or &>).",
        fr="tout.txt doit AUSSI contenir l'erreur : redirige stdout ET stderr "
        "(2>&1 ou &>).",
    )
