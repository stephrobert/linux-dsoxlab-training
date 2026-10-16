"""test_functional.py — l1-prepare-vm (refonte : inventaire matériel réel)

Avant : l'apprenant tapait hostname/distro/kernel/ip en texte libre — jamais
vérifié, et doublon avec l1-01 (kernel/distro) et l1-04 (hostname). Après :
il inventorie les RESSOURCES de sa machine (CPU, mémoire, architecture,
périphérique bloc), chaque champ comparé à l'état réel du système. C'est le
premier réflexe d'un administrateur devant une machine neuve.
"""
from __future__ import annotations

import os
import pathlib
import platform
import re

from conftest import message

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "vm-info.txt"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"


def _read() -> str:
    assert ANSWER_FILE.exists(), message(
        en="vm-info.txt cannot be found. Run: dsoxlab run l1-prepare-vm",
        fr="vm-info.txt introuvable — lance : dsoxlab run l1-prepare-vm",
    )
    return ANSWER_FILE.read_text(encoding="utf-8")


def _field(text: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _real_mem_total_kb() -> int:
    for line in pathlib.Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            return int(re.search(r"(\d+)", line).group(1))
    return -1


def _first_int(value: str) -> int | None:
    m = re.search(r"\d+", value)
    return int(m.group()) if m else None


# ── Présence & complétude ─────────────────────────────────────────────────────

def test_no_placeholder() -> None:
    assert PLACEHOLDER not in _read(), message(
        en=f"The file still contains '{PLACEHOLDER}'. Fill in the 4 fields "
        "with your machine's real values.",
        fr=f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 4 champs "
        "avec les valeurs réelles de ta machine.",
    )


# ── Validation contre l'état RÉEL du système ──────────────────────────────────

def test_cpu_count_matches_real() -> None:
    """CPU_COUNT doit être le nombre réel de CPU (`nproc`)."""
    value = _first_int(_field(_read(), "CPU_COUNT"))
    real = os.cpu_count()
    assert value is not None, message(
        en="CPU_COUNT field empty or not a number. Run: nproc",
        fr="Champ CPU_COUNT vide ou non numérique. Lance : nproc",
    )
    assert value == real, message(
        en=f"CPU_COUNT is '{value}' but your machine has {real} CPU(s). Run `nproc`.",
        fr=f"CPU_COUNT vaut '{value}' mais ta machine a {real} CPU. Lance `nproc`.",
    )


def test_arch_matches_real() -> None:
    """ARCH doit être l'architecture réelle (`uname -m`)."""
    value = _field(_read(), "ARCH")
    real = platform.machine()
    assert value, message(
        en="ARCH field empty. Run: uname -m",
        fr="Champ ARCH vide. Lance : uname -m",
    )
    assert value == real, message(
        en=f"ARCH is '{value}' but the real architecture is '{real}'. "
        "Run `uname -m`.",
        fr=f"ARCH vaut '{value}' mais l'architecture réelle est '{real}'. "
        "Lance `uname -m`.",
    )


def test_mem_total_matches_real() -> None:
    """MEM_TOTAL_KB doit être le MemTotal réel de /proc/meminfo."""
    value = _first_int(_field(_read(), "MEM_TOTAL_KB"))
    real = _real_mem_total_kb()
    assert value is not None, message(
        en="MEM_TOTAL_KB field empty. Run: grep MemTotal /proc/meminfo",
        fr="Champ MEM_TOTAL_KB vide. Lance : grep MemTotal /proc/meminfo",
    )
    assert value == real, message(
        en=f"MEM_TOTAL_KB is '{value}' but the real MemTotal is '{real}' kB. "
        "Take the value from `grep MemTotal /proc/meminfo`.",
        fr=f"MEM_TOTAL_KB vaut '{value}' mais le vrai MemTotal est '{real}' kB. "
        "Relève la valeur de `grep MemTotal /proc/meminfo`.",
    )


def test_block_device_really_exists() -> None:
    """BLOCK_DEVICE doit nommer un périphérique bloc réel (visible dans lsblk)."""
    value = _field(_read(), "BLOCK_DEVICE")
    assert value, message(
        en="BLOCK_DEVICE field empty. Run: lsblk -dno NAME",
        fr="Champ BLOCK_DEVICE vide. Lance : lsblk -dno NAME",
    )
    name = value.split("/")[-1]
    assert (pathlib.Path("/sys/block") / name).exists(), message(
        en=f"'{name}' is not a block device of your machine. "
        "Run `lsblk -dno NAME` and name a real disk (e.g. vda, sda, nvme0n1).",
        fr=f"'{name}' n'est pas un périphérique bloc de ta machine. "
        "Lance `lsblk -dno NAME` et cite un disque réel (ex. vda, sda, nvme0n1).",
    )
