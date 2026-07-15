"""test_functional.py — l1-01-discover-linux-map (refonte : exploration réelle)

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

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "notions.md"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"


def _read() -> str:
    assert ANSWER_FILE.exists(), (
        "notions.md introuvable — lance : dsoxlab run l1-01-discover-linux-map"
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

def test_file_exists() -> None:
    assert ANSWER_FILE.exists(), (
        "notions.md introuvable — lance : dsoxlab run l1-01-discover-linux-map"
    )


def test_no_placeholder() -> None:
    assert PLACEHOLDER not in _read(), (
        f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 4 champs "
        "avec les faits réels de ta machine."
    )


# ── Validation contre l'état RÉEL du système ──────────────────────────────────

def test_kernel_matches_real() -> None:
    """KERNEL doit être la version réelle du noyau (`uname -r`)."""
    value = _field(_read(), "KERNEL")
    real = platform.release()
    assert value, "Champ KERNEL vide. Lance : uname -r"
    assert value == real, (
        f"KERNEL vaut '{value}' mais ton noyau réel est '{real}'. "
        "Lance `uname -r` et colle la sortie exacte."
    )


def test_distro_id_matches_real() -> None:
    """DISTRO_ID doit être l'ID réel de /etc/os-release."""
    value = _field(_read(), "DISTRO_ID").lower()
    real = _real_distro_id()
    assert value, (
        "Champ DISTRO_ID vide. Lance : grep '^ID=' /etc/os-release "
        "(ou : . /etc/os-release ; echo $ID)"
    )
    assert real, "/etc/os-release illisible sur cette machine (cas rare)."
    assert value == real, (
        f"DISTRO_ID vaut '{value}' mais l'ID réel est '{real}'. "
        "Relève la ligne ID= de /etc/os-release."
    )


def test_etc_file_really_exists() -> None:
    """ETC_FILE doit nommer un fichier réellement présent dans /etc."""
    value = _field(_read(), "ETC_FILE")
    assert value, "Champ ETC_FILE vide. Lance : ls /etc — puis cite un fichier."
    name = value.split("/")[-1]
    target = pathlib.Path("/etc") / name
    assert target.is_file(), (
        f"/etc/{name} n'existe pas comme fichier sur ta machine. "
        "Lance `ls /etc` et cite un fichier RÉELLEMENT présent (ex. fstab, hostname)."
    )


def test_log_file_really_exists() -> None:
    """LOG_FILE doit nommer un fichier réellement présent dans /var/log."""
    value = _field(_read(), "LOG_FILE")
    assert value, "Champ LOG_FILE vide. Lance : ls /var/log — puis cite un fichier."
    name = value.split("/")[-1]
    target = pathlib.Path("/var/log") / name
    assert target.exists(), (
        f"/var/log/{name} n'existe pas sur ta machine. Lance `ls /var/log` et "
        "cite un fichier réellement présent (ex. syslog, messages, dmesg)."
    )
