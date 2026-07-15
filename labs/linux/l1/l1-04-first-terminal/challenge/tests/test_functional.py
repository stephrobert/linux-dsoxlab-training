"""test_functional.py — l1-04-first-terminal (refonte : validation de l'état réel)

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

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "premiers-pas.txt"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"


def _read() -> str:
    assert ANSWER_FILE.exists(), (
        "premiers-pas.txt introuvable — lance d'abord : "
        "dsoxlab run l1-04-first-terminal"
    )
    return ANSWER_FILE.read_text(encoding="utf-8")


def _field(text: str, key: str) -> str:
    """Retourne la valeur de la ligne `KEY: valeur`, ou '' si absente."""
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


# ── Présence & complétude ─────────────────────────────────────────────────────

def test_file_exists() -> None:
    """premiers-pas.txt doit exister dans challenge/work/."""
    assert ANSWER_FILE.exists(), (
        "premiers-pas.txt introuvable — lance : dsoxlab run l1-04-first-terminal"
    )


def test_no_placeholder() -> None:
    """Tous les placeholders VOTRE_RÉPONSE_ICI doivent être remplacés."""
    assert PLACEHOLDER not in _read(), (
        f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 4 champs "
        "avec la sortie réelle des commandes."
    )


# ── Validation contre l'état RÉEL du système ──────────────────────────────────

def test_user_matches_real() -> None:
    """USER doit être ton utilisateur réel (sortie de `whoami`)."""
    value = _field(_read(), "USER")
    real = getpass.getuser()
    assert value, "Champ USER vide. Lance : whoami — puis reporte la sortie."
    assert value == real, (
        f"USER vaut '{value}' mais ton utilisateur réel est '{real}'. "
        "Ne devine pas : lance `whoami` et colle la vraie sortie."
    )


def test_machine_matches_real() -> None:
    """MACHINE doit être le nom réel de la machine (sortie de `hostname`)."""
    value = _field(_read(), "MACHINE")
    real = socket.gethostname()
    real_short = real.split(".")[0]
    assert value, "Champ MACHINE vide. Lance : hostname — puis reporte la sortie."
    assert value in (real, real_short), (
        f"MACHINE vaut '{value}' mais le nom réel est '{real}'. "
        "Lance `hostname` et colle la vraie sortie."
    )


def test_home_matches_real() -> None:
    """HOME doit être ton répertoire personnel réel (`echo $HOME`)."""
    value = _field(_read(), "HOME")
    real = str(pathlib.Path.home())
    assert value, "Champ HOME vide. Lance : echo $HOME — puis reporte la sortie."
    assert value.rstrip("/") == real.rstrip("/"), (
        f"HOME vaut '{value}' mais ton home réel est '{real}'. "
        "Lance `echo $HOME` et colle la vraie sortie."
    )


def test_date_is_real() -> None:
    """DATE doit être une vraie sortie de `date` (contient l'année courante)."""
    value = _field(_read(), "DATE")
    year = str(datetime.date.today().year)
    assert value, "Champ DATE vide. Lance : date — puis reporte la sortie."
    assert year in value, (
        f"DATE ('{value}') ne contient pas l'année courante ({year}). "
        "Lance `date` maintenant et colle la sortie fraîche — ne recopie pas "
        "une date d'exemple."
    )


# ── Structure ─────────────────────────────────────────────────────────────────

def test_all_fields_present() -> None:
    """Les 4 clés doivent figurer dans le fichier."""
    text = _read()
    for key in ("USER", "MACHINE", "HOME", "DATE"):
        assert re.search(rf"^{key}:", text, re.MULTILINE), (
            f"La ligne '{key}:' manque dans premiers-pas.txt."
        )
