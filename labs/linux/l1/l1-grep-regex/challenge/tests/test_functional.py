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

from conftest import message

WORK = pathlib.Path(".")
SOURCE = WORK / "acces.log"

IP_RE = re.compile(r"^(?:[0-9]+\.){3}[0-9]+")


def _lines() -> list[str]:
    assert SOURCE.exists(), message(
        en="acces.log cannot be found. Run: dsoxlab run l1-grep-regex",
        fr="acces.log introuvable — lance : dsoxlab run l1-grep-regex",
    )
    return [ln for ln in SOURCE.read_text(encoding="utf-8").splitlines() if ln]


def _read(name: str) -> list[str]:
    f = WORK / name
    assert f.exists(), message(
        en=f"{name} is missing.",
        fr=f"{name} manquant.",
    )
    return [ln for ln in f.read_text(encoding="utf-8").splitlines() if ln]


def test_erreurs_5xx() -> None:
    """erreurs5xx.txt = uniquement les lignes dont le code HTTP est 5xx."""
    f = WORK / "erreurs5xx.txt"
    assert f.exists(), message(
        en="erreurs5xx.txt is missing: keep only the lines of acces.log "
        "whose HTTP code, at the end of the line, is a 5xx.",
        fr="erreurs5xx.txt manquant : garde seulement les lignes d'acces.log "
        "dont le code HTTP, en fin de ligne, est un 5xx.",
    )
    got = _read("erreurs5xx.txt")
    expected = [ln for ln in _lines() if re.search(r" 5\d\d$", ln)]
    assert got == expected, message(
        en=f"erreurs5xx.txt must contain exactly the 5xx lines, in log order. "
        f"Your file has {len(got)} line(s) for {len(expected)} expected"
        + (f"; first differing line: no. {next(i + 1 for i, (a, b) in enumerate(zip(got, expected)) if a != b)}"
           if any(a != b for a, b in zip(got, expected)) else "") + ".",
        fr=f"erreurs5xx.txt doit contenir exactement les lignes 5xx, dans l'ordre du journal. "
        f"Ton fichier compte {len(got)} ligne(s) pour {len(expected)} attendue(s)"
        + (f" ; première ligne différente : n°{next(i + 1 for i, (a, b) in enumerate(zip(got, expected)) if a != b)}"
           if any(a != b for a, b in zip(got, expected)) else "") + ".",
    )


def test_sans_200() -> None:
    """sans-200.txt = toutes les lignes SAUF les 200 (grep -v)."""
    f = WORK / "sans-200.txt"
    assert f.exists(), message(
        en="sans-200.txt is missing: keep every line of acces.log "
        "except those whose HTTP code is 200.",
        fr="sans-200.txt manquant : garde toutes les lignes d'acces.log "
        "sauf celles dont le code HTTP vaut 200.",
    )
    got = _read("sans-200.txt")
    expected = [ln for ln in _lines() if not re.search(r" 200$", ln)]
    assert got == expected, message(
        en=f"sans-200.txt must keep every line except the 200 ones, in log order. "
        f"Your file has {len(got)} line(s) for {len(expected)} expected"
        + (f"; first differing line: no. {next(i + 1 for i, (a, b) in enumerate(zip(got, expected)) if a != b)}"
           if any(a != b for a, b in zip(got, expected)) else "") + ".",
        fr=f"sans-200.txt doit garder toutes les lignes sauf les 200, dans l'ordre du journal. "
        f"Ton fichier compte {len(got)} ligne(s) pour {len(expected)} attendue(s)"
        + (f" ; première ligne différente : n°{next(i + 1 for i, (a, b) in enumerate(zip(got, expected)) if a != b)}"
           if any(a != b for a, b in zip(got, expected)) else "") + ".",
    )


def test_ips_distinctes() -> None:
    """ips.txt = les adresses IP distinctes, triées (grep -oE + sort -u)."""
    f = WORK / "ips.txt"
    assert f.exists(), message(
        en="ips.txt is missing: extract only the IP address of each line, "
        "then keep each address once, sorted.",
        fr="ips.txt manquant : extrais seulement l'adresse IP de chaque ligne, "
        "puis garde chaque adresse une seule fois, triée.",
    )
    got = _read("ips.txt")
    expected = sorted({m.group() for ln in _lines() if (m := IP_RE.match(ln))})
    assert got == expected, message(
        en=f"ips.txt must contain each IP address once, sorted. "
        f"Your file has {len(got)} line(s) for {len(expected)} distinct address(es)"
        + (", with duplicates" if len(set(got)) < len(got) else "")
        + (", not sorted" if got != sorted(got) else "")
        + (", and lines that are more than an address" if any(not IP_RE.fullmatch(ln) for ln in got) else "")
        + ".",
        fr=f"ips.txt doit contenir chaque adresse IP une seule fois, triée. "
        f"Ton fichier compte {len(got)} ligne(s) pour {len(expected)} adresse(s) distincte(s)"
        + (", avec des doublons" if len(set(got)) < len(got) else "")
        + (", sans être trié" if got != sorted(got) else "")
        + (", et des lignes qui contiennent plus qu'une adresse" if any(not IP_RE.fullmatch(ln) for ln in got) else "")
        + ".",
    )


def test_nb_post() -> None:
    """nb-post.txt = le NOMBRE de requêtes POST (grep -c)."""
    f = WORK / "nb-post.txt"
    assert f.exists(), message(
        en="nb-post.txt is missing: it must contain the number of POST requests "
        "in acces.log, not the lines themselves.",
        fr="nb-post.txt manquant : il doit contenir le nombre de requêtes POST "
        "d'acces.log, pas les lignes elles-mêmes.",
    )
    m = re.search(r"\d+", (WORK / "nb-post.txt").read_text(encoding="utf-8"))
    expected = sum(1 for ln in _lines() if " POST " in ln)
    assert m and int(m.group()) == expected, message(
        en="nb-post.txt does not contain the number of POST requests. "
        "Make sure you count the requests, and only the POST ones.",
        fr="nb-post.txt ne contient pas le nombre de requêtes POST. "
        "Vérifie que tu comptes les requêtes, et seulement les POST.",
    )
