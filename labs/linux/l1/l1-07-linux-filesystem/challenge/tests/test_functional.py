"""test_functional.py — l1-07-linux-filesystem (refonte : localiser le réel)

Avant : l'apprenant décrivait « le rôle de /etc » en prose et rangeait des
fichiers fictifs — jamais vérifié contre un système. Après : il LOCALISE de
vrais éléments sur sa machine en s'appuyant sur la FHS, et chaque chemin donné
doit exister réellement à l'endroit attendu. Comprendre la FHS reste l'objet du
cours ; le lab prouve que l'apprenant sait s'y retrouver sur un vrai système.
"""
from __future__ import annotations

import pathlib
import re

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "fhs.txt"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"


def _read() -> str:
    assert ANSWER_FILE.exists(), (
        "fhs.txt introuvable — lance : dsoxlab run l1-07-linux-filesystem"
    )
    return ANSWER_FILE.read_text(encoding="utf-8")


def _field(text: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


# ── Présence & complétude ─────────────────────────────────────────────────────

def test_file_exists() -> None:
    assert ANSWER_FILE.exists(), (
        "fhs.txt introuvable — lance : dsoxlab run l1-07-linux-filesystem"
    )


def test_no_placeholder() -> None:
    assert PLACEHOLDER not in _read(), (
        f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 4 chemins "
        "avec les vrais emplacements de ta machine."
    )


# ── Validation : chaque chemin doit exister RÉELLEMENT au bon endroit FHS ──────

def test_ls_path_is_real() -> None:
    """LS_PATH doit être le chemin absolu réel de `ls` (via `which ls`)."""
    value = _field(_read(), "LS_PATH")
    assert value, "Champ LS_PATH vide. Lance : which ls"
    p = pathlib.Path(value)
    assert p.is_absolute(), f"LS_PATH doit être un chemin absolu (vu : '{value}')."
    assert p.exists(), f"{value} n'existe pas. Lance `which ls` et colle le chemin exact."
    assert p.name == "ls", f"LS_PATH doit pointer la commande ls (vu : '{p.name}')."
    assert "bin" in p.parts, (
        "Les binaires exécutables vivent dans un répertoire bin (FHS). "
        f"Vu : {value}"
    )


def test_user_db_is_real() -> None:
    """USER_DB doit être le fichier réel des comptes : /etc/passwd."""
    value = _field(_read(), "USER_DB").rstrip("/")
    assert value, "Champ USER_DB vide. Le fichier des comptes utilisateurs vit dans /etc."
    assert value == "/etc/passwd", (
        f"USER_DB vaut '{value}' — la base des comptes locaux est /etc/passwd (FHS : "
        "la configuration système est dans /etc)."
    )
    assert pathlib.Path("/etc/passwd").exists(), "/etc/passwd absent (cas très rare)."


def test_log_dir_is_real() -> None:
    """LOG_DIR doit être le répertoire réel des journaux système : /var/log."""
    value = _field(_read(), "LOG_DIR").rstrip("/")
    assert value, "Champ LOG_DIR vide. Les journaux système vivent dans /var."
    assert value == "/var/log", (
        f"LOG_DIR vaut '{value}' — les journaux système sont dans /var/log (FHS : "
        "données variables sous /var)."
    )
    assert pathlib.Path("/var/log").is_dir(), "/var/log absent (cas très rare)."


def test_home_parent_is_real() -> None:
    """HOME_PARENT doit être le répertoire réel parent des homes : /home."""
    value = _field(_read(), "HOME_PARENT").rstrip("/")
    assert value, "Champ HOME_PARENT vide. Les répertoires personnels vivent sous /home."
    assert value == "/home", (
        f"HOME_PARENT vaut '{value}' — les homes des utilisateurs standard sont "
        "sous /home (FHS)."
    )
    assert pathlib.Path("/home").is_dir(), "/home absent sur cette machine."
