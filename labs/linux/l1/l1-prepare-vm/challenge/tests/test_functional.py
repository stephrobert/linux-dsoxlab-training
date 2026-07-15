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

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "vm-info.txt"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"


def _read() -> str:
    assert ANSWER_FILE.exists(), (
        "vm-info.txt introuvable — lance : dsoxlab run l1-prepare-vm"
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

def test_file_exists() -> None:
    assert ANSWER_FILE.exists(), (
        "vm-info.txt introuvable — lance : dsoxlab run l1-prepare-vm"
    )


def test_no_placeholder() -> None:
    assert PLACEHOLDER not in _read(), (
        f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 4 champs "
        "avec les valeurs réelles de ta machine."
    )


# ── Validation contre l'état RÉEL du système ──────────────────────────────────

def test_cpu_count_matches_real() -> None:
    """CPU_COUNT doit être le nombre réel de CPU (`nproc`)."""
    value = _first_int(_field(_read(), "CPU_COUNT"))
    real = os.cpu_count()
    assert value is not None, "Champ CPU_COUNT vide ou non numérique. Lance : nproc"
    assert value == real, (
        f"CPU_COUNT vaut '{value}' mais ta machine a {real} CPU. Lance `nproc`."
    )


def test_arch_matches_real() -> None:
    """ARCH doit être l'architecture réelle (`uname -m`)."""
    value = _field(_read(), "ARCH")
    real = platform.machine()
    assert value, "Champ ARCH vide. Lance : uname -m"
    assert value == real, (
        f"ARCH vaut '{value}' mais l'architecture réelle est '{real}'. "
        "Lance `uname -m`."
    )


def test_mem_total_matches_real() -> None:
    """MEM_TOTAL_KB doit être le MemTotal réel de /proc/meminfo."""
    value = _first_int(_field(_read(), "MEM_TOTAL_KB"))
    real = _real_mem_total_kb()
    assert value is not None, (
        "Champ MEM_TOTAL_KB vide. Lance : grep MemTotal /proc/meminfo"
    )
    assert value == real, (
        f"MEM_TOTAL_KB vaut '{value}' mais le vrai MemTotal est '{real}' kB. "
        "Relève la valeur de `grep MemTotal /proc/meminfo`."
    )


def test_block_device_really_exists() -> None:
    """BLOCK_DEVICE doit nommer un périphérique bloc réel (visible dans lsblk)."""
    value = _field(_read(), "BLOCK_DEVICE")
    assert value, "Champ BLOCK_DEVICE vide. Lance : lsblk -dno NAME"
    name = value.split("/")[-1]
    assert (pathlib.Path("/sys/block") / name).exists(), (
        f"'{name}' n'est pas un périphérique bloc de ta machine. "
        "Lance `lsblk -dno NAME` et cite un disque réel (ex. vda, sda, nvme0n1)."
    )
