"""test_functional.py : l1-first-terminal, validation de l'état réel

Principe : un lab prouve un état, il ne fait pas confiance au texte saisi.
Ce lab tourne en runtime shell, donc sur la machine de l'apprenant. Chaque
champ de premiers-pas.txt est comparé à la VALEUR RÉELLE du système
(`getpass.getuser()`, `socket.gethostname()`, `Path.home()`, l'horloge). Un
apprenant qui invente une valeur au lieu de lancer la commande échoue.
"""
from __future__ import annotations

import datetime
import getpass
import pathlib
import re
import socket

from conftest import message

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "premiers-pas.txt"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"
#: Une ligne de l'en-tête fourni. Elle ne survit QUE si le fichier a été
#: édité : une redirection « > » le recrée de zéro et l'emporte.
SENTINELLE_EN_TETE = "N'efface pas ces lignes d'en-tête"


def _read() -> str:
    assert ANSWER_FILE.exists(), message(
        en="premiers-pas.txt cannot be found. Run this first: "
        "dsoxlab run l1-first-terminal",
        fr="premiers-pas.txt introuvable. Lance d'abord : "
        "dsoxlab run l1-first-terminal",
    )
    return ANSWER_FILE.read_text(encoding="utf-8")


def _field(text: str, key: str) -> str:
    """Retourne la valeur de la ligne `KEY: valeur`, ou '' si absente."""
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


# ── Présence & complétude ─────────────────────────────────────────────────────

def test_no_placeholder() -> None:
    """Tous les placeholders VOTRE_RÉPONSE_ICI doivent être remplacés."""
    assert PLACEHOLDER not in _read(), message(
        en=f"The file still contains '{PLACEHOLDER}'. Fill in the 4 fields "
        "with the commands' real output.",
        fr=f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 4 champs "
        "avec la sortie réelle des commandes.",
    )


def test_le_fichier_a_ete_edite_et_non_recree() -> None:
    """L'en-tête fourni doit avoir survécu : on ÉDITE, on ne recrée pas.

    C'est la contrainte que l'énoncé annonce. Sans ce test, elle était fausse :
    recréer le fichier avec « > » donnait 100/100, et une contrainte annoncée
    que rien ne tient apprend à ignorer les contraintes.
    """
    assert SENTINELLE_EN_TETE in _read(), message(
        en="The provided header is gone from premiers-pas.txt. It only "
        "disappears when the file is RECREATED, typically with a `>` "
        "redirection, which wipes everything in it. Open the file in an editor "
        "(nano, vim) and change the four values in place: `dsoxlab reset "
        "l1-first-terminal` gives you the starting file back.",
        fr="L'en-tête fourni a disparu de premiers-pas.txt. Il ne disparaît que "
        "si le fichier a été RECRÉÉ, typiquement avec une redirection « > », "
        "qui en efface tout le contenu. Ouvre le fichier dans un éditeur "
        "(nano, vim) et change les quatre valeurs sur place : `dsoxlab reset "
        "l1-first-terminal` te rend le fichier de départ.",
    )


# ── Validation contre l'état RÉEL du système ──────────────────────────────────

def test_user_matches_real() -> None:
    """USER doit être ton utilisateur réel (sortie de `whoami`)."""
    value = _field(_read(), "USER")
    real = getpass.getuser()
    assert value, message(
        en="USER field empty. Run: whoami, then report the output.",
        fr="Champ USER vide. Lance `whoami`, puis reporte la sortie.",
    )
    assert value == real, message(
        en=f"USER is '{value}' but your real user is '{real}'. "
        "Do not guess: run `whoami` and paste the real output.",
        fr=f"USER vaut '{value}' mais ton utilisateur réel est '{real}'. "
        "Ne devine pas : lance `whoami` et colle la vraie sortie.",
    )


def test_machine_matches_real() -> None:
    """MACHINE doit être le nom réel de la machine (sortie de `hostname`)."""
    value = _field(_read(), "MACHINE")
    real = socket.gethostname()
    real_short = real.split(".")[0]
    assert value, message(
        en="MACHINE field empty. Run: hostname, then report the output.",
        fr="Champ MACHINE vide. Lance `hostname`, puis reporte la sortie.",
    )
    assert value in (real, real_short), message(
        en=f"MACHINE is '{value}' but the real name is '{real}'. "
        "Run `hostname` and paste the real output.",
        fr=f"MACHINE vaut '{value}' mais le nom réel est '{real}'. "
        "Lance `hostname` et colle la vraie sortie.",
    )


def test_home_matches_real() -> None:
    """HOME doit être ton répertoire personnel réel (`echo $HOME`)."""
    value = _field(_read(), "HOME")
    real = str(pathlib.Path.home())
    assert value, message(
        en="HOME field empty. Run: echo $HOME, then report the output.",
        fr="Champ HOME vide. Lance `echo $HOME`, puis reporte la sortie.",
    )
    assert value.rstrip("/") == real.rstrip("/"), message(
        en=f"HOME is '{value}' but your real home is '{real}'. "
        "Run `echo $HOME` and paste the real output.",
        fr=f"HOME vaut '{value}' mais ton home réel est '{real}'. "
        "Lance `echo $HOME` et colle la vraie sortie.",
    )


def test_date_is_real() -> None:
    """DATE doit être une vraie sortie de `date` (contient l'année courante)."""
    value = _field(_read(), "DATE")
    # `date.today()` lit l'horloge locale sans fuseau explicite ; on veut
    # l'année telle que la machine du lab la voit, donc son heure locale
    # assumée, pas une conversion implicite.
    year = str(datetime.datetime.now().astimezone().year)
    assert value, message(
        en="DATE field empty. Run: date, then report the output.",
        fr="Champ DATE vide. Lance `date`, puis reporte la sortie.",
    )
    assert year in value, message(
        en=f"DATE ('{value}') does not contain the current year ({year}). "
        "Run `date` now and paste the fresh output; do not copy "
        "an example date.",
        fr=f"DATE ('{value}') ne contient pas l'année courante ({year}). "
        "Lance `date` maintenant et colle la sortie fraîche, ne recopie pas "
        "une date d'exemple.",
    )


# ── Structure ─────────────────────────────────────────────────────────────────
