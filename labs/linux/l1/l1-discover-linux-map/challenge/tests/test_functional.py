"""test_functional.py — l1-discover-linux-map (refonte : exploration réelle)

Avant : l'apprenant écrivait de la prose « avec ses mots », impossible à
valider. Après : il EXPLORE sa machine et capture des faits réels, comparés à
l'état du système (kernel, ID de distribution, fichiers réellement présents
dans /etc et /var/log). Comprendre les concepts reste l'objet du cours et du
quiz ; le lab, lui, prouve que l'apprenant a réellement exploré son système.
"""
from __future__ import annotations

import pathlib
import platform
import re

from conftest import message

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "notions.md"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"


def _read() -> str:
    assert ANSWER_FILE.exists(), message(
        en="notions.md cannot be found. Run: dsoxlab run l1-discover-linux-map",
        fr="notions.md introuvable — lance : dsoxlab run l1-discover-linux-map",
    )
    return ANSWER_FILE.read_text(encoding="utf-8")


def _field(text: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _real_distro_id() -> str:
    """Lit l'ID réel dans /etc/os-release (ex. 'debian', 'ubuntu', 'almalinux')."""
    osr = pathlib.Path("/etc/os-release")
    if not osr.exists():
        return ""
    for line in osr.read_text(encoding="utf-8").splitlines():
        if line.startswith("ID="):
            return line.split("=", 1)[1].strip().strip('"').lower()
    return ""


# ── Présence & complétude ─────────────────────────────────────────────────────

def test_no_placeholder() -> None:
    assert PLACEHOLDER not in _read(), message(
        en=f"The file still contains '{PLACEHOLDER}'. Fill in the 4 fields "
        "with your machine's real facts.",
        fr=f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 4 champs "
        "avec les faits réels de ta machine.",
    )


# ── Validation contre l'état RÉEL du système ──────────────────────────────────

def test_kernel_matches_real() -> None:
    """KERNEL doit être la version réelle du noyau (`uname -r`)."""
    value = _field(_read(), "KERNEL")
    real = platform.release()
    assert value, message(
        en="KERNEL field empty. Run: uname -r",
        fr="Champ KERNEL vide. Lance : uname -r",
    )
    assert value == real, message(
        en=f"KERNEL is '{value}' but your real kernel is '{real}'. "
        "Run `uname -r` and paste the exact output.",
        fr=f"KERNEL vaut '{value}' mais ton noyau réel est '{real}'. "
        "Lance `uname -r` et colle la sortie exacte.",
    )


def test_distro_id_matches_real() -> None:
    """DISTRO_ID doit être l'ID réel de /etc/os-release."""
    value = _field(_read(), "DISTRO_ID").lower()
    real = _real_distro_id()
    assert value, message(
        en="DISTRO_ID field empty. Run: grep '^ID=' /etc/os-release "
        "(or: . /etc/os-release ; echo $ID)",
        fr="Champ DISTRO_ID vide. Lance : grep '^ID=' /etc/os-release "
        "(ou : . /etc/os-release ; echo $ID)",
    )
    assert real, message(
        en="/etc/os-release cannot be read on this machine (a rare case).",
        fr="/etc/os-release illisible sur cette machine (cas rare).",
    )
    assert value == real, message(
        en=f"DISTRO_ID is '{value}' but the real ID is '{real}'. "
        "Take the ID= line from /etc/os-release.",
        fr=f"DISTRO_ID vaut '{value}' mais l'ID réel est '{real}'. "
        "Relève la ligne ID= de /etc/os-release.",
    )


def test_etc_file_really_exists() -> None:
    """ETC_FILE doit nommer un fichier réellement présent dans /etc."""
    value = _field(_read(), "ETC_FILE")
    assert value, message(
        en="ETC_FILE field empty. Run: ls /etc, then name a file.",
        fr="Champ ETC_FILE vide. Lance : ls /etc — puis cite un fichier.",
    )
    name = value.split("/")[-1]
    target = pathlib.Path("/etc") / name
    assert target.is_file(), message(
        en=f"/etc/{name} does not exist as a file on your machine. "
        "Run `ls /etc` and name a file that is ACTUALLY there (e.g. fstab, hostname).",
        fr=f"/etc/{name} n'existe pas comme fichier sur ta machine. "
        "Lance `ls /etc` et cite un fichier RÉELLEMENT présent (ex. fstab, hostname).",
    )


def test_log_file_really_exists() -> None:
    """LOG_FILE doit nommer un fichier réellement présent dans /var/log."""
    value = _field(_read(), "LOG_FILE")
    assert value, message(
        en="LOG_FILE field empty. Run: ls /var/log, then name a file.",
        fr="Champ LOG_FILE vide. Lance : ls /var/log — puis cite un fichier.",
    )
    name = value.split("/")[-1]
    target = pathlib.Path("/var/log") / name
    assert target.exists(), message(
        en=f"/var/log/{name} does not exist on your machine. Run `ls /var/log` and "
        "name a file that is actually there (e.g. syslog, messages, dmesg).",
        fr=f"/var/log/{name} n'existe pas sur ta machine. Lance `ls /var/log` et "
        "cite un fichier réellement présent (ex. syslog, messages, dmesg).",
    )
