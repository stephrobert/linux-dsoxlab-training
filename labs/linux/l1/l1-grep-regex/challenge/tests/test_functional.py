"""test_functional.py — l1-grep-regex

Prouve l'ÉTAT (les artefacts réellement produits par grep), pas les commandes
tapées. Chaque attendu est recalculé depuis `acces.log`, donc le test ne fait
confiance à aucune valeur codée en dur.

Point de départ : `acces.log` (10 lignes « IP - METHODE /chemin CODE »), copié
par `dsoxlab run`.
"""
from __future__ import annotations

import pathlib
import re

WORK = pathlib.Path(".")
SOURCE = WORK / "acces.log"

IP_RE = re.compile(r"^(?:[0-9]+\.){3}[0-9]+")


def _lines() -> list[str]:
    assert SOURCE.exists(), (
        "acces.log introuvable — lance : dsoxlab run l1-grep-regex"
    )
    return [ln for ln in SOURCE.read_text(encoding="utf-8").splitlines() if ln]


def _read(name: str) -> list[str]:
    f = WORK / name
    assert f.exists(), f"{name} manquant."
    return [ln for ln in f.read_text(encoding="utf-8").splitlines() if ln]


def test_source_present() -> None:
    assert SOURCE.exists(), (
        "acces.log introuvable — lance : dsoxlab run l1-grep-regex"
    )


def test_erreurs_5xx() -> None:
    """erreurs5xx.txt = uniquement les lignes dont le code HTTP est 5xx."""
    f = WORK / "erreurs5xx.txt"
    assert f.exists(), (
        "erreurs5xx.txt manquant. Filtre les codes 5xx en fin de ligne : "
        "grep -E ' 5[0-9][0-9]$' acces.log > erreurs5xx.txt"
    )
    got = _read("erreurs5xx.txt")
    expected = [ln for ln in _lines() if re.search(r" 5\d\d$", ln)]
    assert got == expected, (
        f"erreurs5xx.txt doit contenir les lignes 5xx.\n"
        f"Attendu : {expected}\nObtenu : {got}"
    )


def test_sans_200() -> None:
    """sans-200.txt = toutes les lignes SAUF les 200 (grep -v)."""
    f = WORK / "sans-200.txt"
    assert f.exists(), (
        "sans-200.txt manquant. Inverse le filtre : "
        "grep -v ' 200$' acces.log > sans-200.txt"
    )
    got = _read("sans-200.txt")
    expected = [ln for ln in _lines() if not re.search(r" 200$", ln)]
    assert got == expected, (
        f"sans-200.txt doit exclure les lignes 200.\n"
        f"Attendu : {expected}\nObtenu : {got}"
    )


def test_ips_distinctes() -> None:
    """ips.txt = les adresses IP distinctes, triées (grep -oE + sort -u)."""
    f = WORK / "ips.txt"
    assert f.exists(), (
        "ips.txt manquant. Extrais puis dédoublonne : "
        "grep -oE '^([0-9]+\\.){3}[0-9]+' acces.log | sort -u > ips.txt"
    )
    got = _read("ips.txt")
    expected = sorted({m.group() for ln in _lines() if (m := IP_RE.match(ln))})
    assert got == expected, (
        f"ips.txt doit contenir les IP distinctes triées.\n"
        f"Attendu : {expected}\nObtenu : {got}"
    )


def test_nb_post() -> None:
    """nb-post.txt = le NOMBRE de requêtes POST (grep -c)."""
    f = WORK / "nb-post.txt"
    assert f.exists(), (
        "nb-post.txt manquant. Compte : grep -cE ' POST ' acces.log > nb-post.txt"
    )
    m = re.search(r"\d+", (WORK / "nb-post.txt").read_text(encoding="utf-8"))
    expected = sum(1 for ln in _lines() if " POST " in ln)
    assert m and int(m.group()) == expected, (
        f"nb-post.txt doit contenir le nombre de POST ({expected}). "
        "Utilise : grep -cE ' POST ' acces.log > nb-post.txt"
    )
