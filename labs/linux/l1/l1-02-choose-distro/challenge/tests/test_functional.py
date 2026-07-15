"""test_functional.py — l1-02-choose-distro (refonte : écosystème réel)

Avant : l'apprenant « choisissait » une distribution et justifiait en prose —
une décision, rien à prouver sur un système. Après : il identifie l'ÉCOSYSTÈME
RÉEL de sa machine (famille, gestionnaire de paquets, commande d'installation),
chaque réponse comparée à ce que la machine expose vraiment. Comprendre en quoi
les familles diffèrent reste l'objet du cours ; le lab prouve que l'apprenant
sait reconnaître la sienne.
"""
from __future__ import annotations

import pathlib
import re
import shutil

WORK = pathlib.Path(".")
ANSWER_FILE = WORK / "choix-distro.txt"
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"

KNOWN_MANAGERS = {"apt", "apt-get", "dnf", "yum", "zypper", "pacman", "apk"}
FAMILY_MANAGERS = {
    "debian": {"apt", "apt-get"},
    "rhel": {"dnf", "yum"},
    "suse": {"zypper"},
    "arch": {"pacman"},
    "alpine": {"apk"},
}


def _read() -> str:
    assert ANSWER_FILE.exists(), (
        "choix-distro.txt introuvable — lance : dsoxlab run l1-02-choose-distro"
    )
    return ANSWER_FILE.read_text(encoding="utf-8")


def _field(text: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _osr() -> dict[str, str]:
    data: dict[str, str] = {}
    osr = pathlib.Path("/etc/os-release")
    if osr.exists():
        for line in osr.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k] = v.strip().strip('"').lower()
    return data


def _real_family() -> str:
    """Déduit la famille réelle (debian/rhel/suse/arch/alpine) de /etc/os-release."""
    osr = _osr()
    tokens = f"{osr.get('ID', '')} {osr.get('ID_LIKE', '')}"
    for family, keys in {
        "debian": ("debian", "ubuntu"),
        "rhel": ("rhel", "fedora", "centos"),
        "suse": ("suse", "opensuse"),
        "arch": ("arch",),
        "alpine": ("alpine",),
    }.items():
        if any(k in tokens for k in keys):
            return family
    return ""


def _real_manager() -> str:
    for mgr in ("apt", "dnf", "yum", "zypper", "pacman", "apk"):
        if shutil.which(mgr):
            return mgr
    return ""


# ── Présence & complétude ─────────────────────────────────────────────────────

def test_file_exists() -> None:
    assert ANSWER_FILE.exists(), (
        "choix-distro.txt introuvable — lance : dsoxlab run l1-02-choose-distro"
    )


def test_no_placeholder() -> None:
    assert PLACEHOLDER not in _read(), (
        f"Le fichier contient encore '{PLACEHOLDER}'. Renseigne les 3 champs "
        "avec ce que ta machine expose réellement."
    )


# ── Validation contre l'état RÉEL du système ──────────────────────────────────

def test_family_matches_real() -> None:
    """FAMILY doit être la famille réelle de ta distribution (via /etc/os-release)."""
    value = _field(_read(), "FAMILY").lower()
    real = _real_family()
    assert value, (
        "Champ FAMILY vide. Lance : grep -E '^ID=|^ID_LIKE=' /etc/os-release"
    )
    assert real, "/etc/os-release illisible (cas rare)."
    assert value == real, (
        f"FAMILY vaut '{value}' mais ta machine est de la famille '{real}'. "
        "Déduis-la de ID / ID_LIKE dans /etc/os-release."
    )


def test_package_manager_is_real() -> None:
    """PACKAGE_MANAGER doit être un gestionnaire réellement présent sur la machine."""
    value = _field(_read(), "PACKAGE_MANAGER").lower()
    assert value, "Champ PACKAGE_MANAGER vide. Cherche apt, dnf, zypper, pacman, apk…"
    assert value in KNOWN_MANAGERS, (
        f"'{value}' n'est pas un gestionnaire de paquets connu. "
        f"Attendus : {', '.join(sorted(KNOWN_MANAGERS))}."
    )
    assert shutil.which(value), (
        f"'{value}' n'est pas installé sur cette machine. Cite celui qui existe "
        "réellement ici (teste avec `which apt`, `which dnf`…)."
    )


def test_install_cmd_uses_real_manager() -> None:
    """INSTALL_CMD doit utiliser le gestionnaire réel de la machine."""
    value = _field(_read(), "INSTALL_CMD").lower()
    real_mgr = _real_manager()
    assert value, (
        "Champ INSTALL_CMD vide. Écris la commande d'installation d'un paquet "
        "avec le gestionnaire de ta machine."
    )
    assert real_mgr and real_mgr in value, (
        f"INSTALL_CMD ('{value}') doit utiliser le gestionnaire réel de cette "
        f"machine : '{real_mgr}'. Ex. : {real_mgr} install <paquet>."
    )
    assert re.search(r"install|add|-s\b", value), (
        "INSTALL_CMD doit être une commande d'INSTALLATION (install / add / -S)."
    )
