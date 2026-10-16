"""test_functional.py — l1-text-processing

Prouve l'ÉTAT (les artefacts réellement produits), pas les commandes tapées.
Chaque attendu est recalculé depuis `ventes.csv`, jamais codé en dur.

Point de départ : `ventes.csv` (8 lignes « date;region;produit;montant »),
copié par `dsoxlab run`.
"""
from __future__ import annotations

import collections
import pathlib

from conftest import message

WORK = pathlib.Path(".")
SOURCE = WORK / "ventes.csv"


def _rows() -> list[list[str]]:
    assert SOURCE.exists(), message(
        en="ventes.csv cannot be found. Run: dsoxlab run l1-text-processing",
        fr="ventes.csv introuvable — lance : dsoxlab run l1-text-processing",
    )
    return [
        ln.split(";")
        for ln in SOURCE.read_text(encoding="utf-8").splitlines()
        if ln
    ]


def _read_lines(name: str) -> list[str]:
    f = WORK / name
    assert f.exists(), message(
        en=f"{name} is missing.",
        fr=f"{name} manquant.",
    )
    return [ln for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_regions_distinctes() -> None:
    """regions.txt = la colonne region, distincte et triée (cut + sort -u)."""
    f = WORK / "regions.txt"
    assert f.exists(), message(
        en="regions.txt is missing. Cut column 2: "
        "cut -d';' -f2 ventes.csv | sort -u > regions.txt",
        fr="regions.txt manquant. Découpe la colonne 2 : "
        "cut -d';' -f2 ventes.csv | sort -u > regions.txt",
    )
    got = _read_lines("regions.txt")
    expected = sorted({r[1] for r in _rows()})
    assert got == expected, message(
        en=f"regions.txt must list the distinct regions, sorted.\n"
        f"Expected: {expected}\nGot: {got}",
        fr=f"regions.txt doit lister les régions distinctes triées.\n"
        f"Attendu : {expected}\nObtenu : {got}",
    )


def test_nb_par_region() -> None:
    """nb-par-region.txt = comptage par région (cut + sort + uniq -c)."""
    f = WORK / "nb-par-region.txt"
    assert f.exists(), message(
        en="nb-par-region.txt is missing. Count by region: "
        "cut -d';' -f2 ventes.csv | sort | uniq -c > nb-par-region.txt",
        fr="nb-par-region.txt manquant. Compte par région : "
        "cut -d';' -f2 ventes.csv | sort | uniq -c > nb-par-region.txt",
    )
    # uniq -c produit « <nb> <region> » avec des espaces variables : on normalise.
    got: dict[str, int] = {}
    for ln in _read_lines("nb-par-region.txt"):
        parts = ln.split()
        assert len(parts) == 2 and parts[0].isdigit(), message(
            en=f"unexpected line in nb-par-region.txt: {ln!r} "
            "(expected format \"<count> <region>\", produced by uniq -c)",
            fr=f"ligne inattendue dans nb-par-region.txt : {ln!r} "
            "(format attendu « <nombre> <region> », produit par uniq -c)",
        )
        got[parts[1]] = int(parts[0])
    expected = dict(collections.Counter(r[1] for r in _rows()))
    assert got == expected, message(
        en=f"Count by region is wrong.\nExpected: {expected}\nGot: {got}",
        fr=f"Comptage par région incorrect.\nAttendu : {expected}\nObtenu : {got}",
    )


def test_total_montant() -> None:
    """total.txt = la somme de la colonne montant (awk)."""
    f = WORK / "total.txt"
    assert f.exists(), message(
        en="total.txt is missing. Sum column 4: "
        "awk -F';' '{s+=$4} END{print s}' ventes.csv > total.txt",
        fr="total.txt manquant. Somme la colonne 4 : "
        "awk -F';' '{s+=$4} END{print s}' ventes.csv > total.txt",
    )
    content = f.read_text(encoding="utf-8").strip()
    expected = sum(int(r[3]) for r in _rows())
    assert content.isdigit() and int(content) == expected, message(
        en=f"total.txt must contain the sum of the amounts ({expected}). Got: {content!r}",
        fr=f"total.txt doit contenir la somme des montants ({expected}). Obtenu : {content!r}",
    )


def test_en_csv() -> None:
    """en-csv.txt = le fichier avec ';' remplacé par ',' (sed)."""
    f = WORK / "en-csv.txt"
    assert f.exists(), message(
        en="en-csv.txt is missing. Replace the separator: "
        "sed 's/;/,/g' ventes.csv > en-csv.txt",
        fr="en-csv.txt manquant. Remplace le séparateur : "
        "sed 's/;/,/g' ventes.csv > en-csv.txt",
    )
    got = _read_lines("en-csv.txt")
    expected = [",".join(r) for r in _rows()]
    assert got == expected, message(
        en=f"en-csv.txt must replace every ';' with ','.\n"
        f"Expected: {expected}\nGot: {got}",
        fr=f"en-csv.txt doit remplacer chaque ';' par ','.\n"
        f"Attendu : {expected}\nObtenu : {got}",
    )
