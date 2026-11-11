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
        en="regions.txt is missing: build it from the region column of "
        "ventes.csv, one region per line, no duplicate, sorted.",
        fr="regions.txt manquant : construis-le à partir de la colonne des "
        "régions de ventes.csv, une région par ligne, sans doublon, triée.",
    )
    got = _read_lines("regions.txt")
    expected = sorted({r[1] for r in _rows()})
    assert got == expected, message(
        en=f"regions.txt must list each region once, sorted. "
        f"Your file has {len(got)} line(s) for {len(expected)} distinct region(s)"
        + (", with duplicates" if len(set(got)) < len(got) else "")
        + (", not sorted" if got != sorted(got) else "")
        + (f", and values that are not regions of ventes.csv: {sorted(set(got) - set(expected))}"
           if set(got) - set(expected) else "") + ".",
        fr=f"regions.txt doit lister chaque région une seule fois, triée. "
        f"Ton fichier compte {len(got)} ligne(s) pour {len(expected)} région(s) distincte(s)"
        + (", avec des doublons" if len(set(got)) < len(got) else "")
        + (", sans être trié" if got != sorted(got) else "")
        + (f", et des valeurs qui ne sont pas des régions de ventes.csv : {sorted(set(got) - set(expected))}"
           if set(got) - set(expected) else "") + ".",
    )


def test_nb_par_region() -> None:
    """nb-par-region.txt = comptage par région (cut + sort + uniq -c)."""
    f = WORK / "nb-par-region.txt"
    assert f.exists(), message(
        en="nb-par-region.txt is missing: count the sales of each region, "
        "one \"<count> <region>\" line per region.",
        fr="nb-par-region.txt manquant : compte les ventes de chaque région, "
        "une ligne « <nombre> <region> » par région.",
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
        en="Count by region is wrong for: "
        + ", ".join(sorted(k for k in set(got) | set(expected) if got.get(k) != expected.get(k)))
        + ". Check that the lines were sorted before being counted.",
        fr="Comptage par région incorrect pour : "
        + ", ".join(sorted(k for k in set(got) | set(expected) if got.get(k) != expected.get(k)))
        + ". Vérifie que les lignes ont été triées avant d'être comptées.",
    )


def test_total_montant() -> None:
    """total.txt = la somme de la colonne montant (awk)."""
    f = WORK / "total.txt"
    assert f.exists(), message(
        en="total.txt is missing: it must contain the sum of the amount "
        "column of ventes.csv, and nothing else.",
        fr="total.txt manquant : il doit contenir la somme de la colonne des "
        "montants de ventes.csv, et rien d'autre.",
    )
    content = f.read_text(encoding="utf-8").strip()
    expected = sum(int(r[3]) for r in _rows())
    assert content.isdigit() and int(content) == expected, message(
        en=f"total.txt does not contain the sum of the amount column. Got: {content!r}. "
        "Check the separator and the column number.",
        fr=f"total.txt ne contient pas la somme de la colonne des montants. Obtenu : {content!r}. "
        "Vérifie le séparateur et le numéro de colonne.",
    )


def test_en_csv() -> None:
    """en-csv.txt = le fichier avec ';' remplacé par ',' (sed)."""
    f = WORK / "en-csv.txt"
    assert f.exists(), message(
        en="en-csv.txt is missing: it is ventes.csv with every ';' "
        "replaced by ','.",
        fr="en-csv.txt manquant : c'est ventes.csv avec chaque « ; » "
        "remplacé par « , ».",
    )
    got = _read_lines("en-csv.txt")
    expected = [",".join(r) for r in _rows()]
    assert got == expected, message(
        en=f"en-csv.txt must repeat ventes.csv line by line, every ';' replaced by ','. "
        f"Your file has {len(got)} line(s) for {len(expected)} expected"
        + (f"; first differing line: no. {next(i + 1 for i, (a, b) in enumerate(zip(got, expected)) if a != b)}"
           if any(a != b for a, b in zip(got, expected)) else "")
        + (" (some ';' are left: is the replacement global?)" if any(";" in ln for ln in got) else "")
        + ".",
        fr=f"en-csv.txt doit reprendre ventes.csv ligne à ligne, chaque « ; » remplacé par « , ». "
        f"Ton fichier compte {len(got)} ligne(s) pour {len(expected)} attendue(s)"
        + (f" ; première ligne différente : n°{next(i + 1 for i, (a, b) in enumerate(zip(got, expected)) if a != b)}"
           if any(a != b for a, b in zip(got, expected)) else "")
        + (" (il reste des « ; » : le remplacement est-il global ?)" if any(";" in ln for ln in got) else "")
        + ".",
    )
