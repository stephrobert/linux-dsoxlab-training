"""Toute collection Ansible employée doit être déclarée dans requirements.yml.

Raison d'être (issue #50) : trois collections hors `ansible.builtin` étaient
utilisées et aucune n'était déclarée. Deux se trouvaient installées par hasard
sur la machine de développement, la troisième non, et le capstone
`rhcsa-mock-exam` échouait alors sur un « rc=4, Stats : {} », le code
« unreachable » d'Ansible, qui envoie chercher un problème de réseau pendant que
la cause est une dépendance absente.

Le contrôle porte sur ce que les fichiers **emploient**, pas sur ce que la
machine a d'installé : une suite qui passe parce que la machine est bien garnie
ne dit rien de celle du prochain qui clone.

Les solutions sont chiffrées par ansible-vault. Sans `.vault-pass`, elles ne sont
pas lisibles : le test le dit et se limite alors à `labs/`, plutôt que de rendre
un vert qui n'aurait rien vérifié.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parent.parent
REQUIREMENTS = RACINE / "requirements.yml"
VAULT_PASS = RACINE / ".vault-pass"

#: Un module en **position de clé** dans une tâche YAML :
#:
#:     - name: …
#:       community.crypto.openssh_keypair:
#:
#: Chercher le motif n'importe où dans le texte ne marche pas : un premier jet le
#: faisait, et remontait `auto.master`, `logs.tar`, `net.ipv4` ou `dl.flathub` :
#: des chemins, des archives et un nom de domaine. Un garde-fou qui crie au loup
#: se fait désactiver, donc il ne regarde que là où un module peut se trouver.
QUALIFIE = re.compile(
    r"^\s*(?:-\s+)?([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)\.[a-z][a-z0-9_]*\s*:",
    re.MULTILINE,
)

#: Fournie avec ansible-core, jamais à déclarer.
INTEGREE = {"ansible.builtin"}


def _declarees() -> set[str]:
    if not REQUIREMENTS.is_file():
        pytest.fail(
            "requirements.yml est absent : les collections employées ne sont "
            "déclarées nulle part, et leur absence se manifestera par un rc=4 "
            "qui ressemble à un problème de réseau."
        )
    contenu = yaml.safe_load(REQUIREMENTS.read_text(encoding="utf-8")) or {}
    return {
        entree["name"] if isinstance(entree, dict) else str(entree)
        for entree in (contenu.get("collections") or [])
    }


def _texte(fichier: Path) -> str:
    """Rend le contenu, en déchiffrant si le fichier est sous vault."""
    brut = fichier.read_bytes()
    if not brut.startswith(b"$ANSIBLE_VAULT"):
        return brut.decode("utf-8", errors="replace")
    if not VAULT_PASS.is_file():
        return ""
    vu = subprocess.run(
        ["ansible-vault", "view", "--vault-password-file", str(VAULT_PASS), str(fichier)],
        capture_output=True,
        text=True,
        check=False,
    )
    return vu.stdout if vu.returncode == 0 else ""


def _employees(racines: list[Path]) -> dict[str, set[str]]:
    """Rend {collection: {fichiers qui l'emploient}}."""
    trouvees: dict[str, set[str]] = {}
    for racine in racines:
        if not racine.is_dir():
            continue
        for fichier in list(racine.rglob("*.yaml")) + list(racine.rglob("*.yml")):
            for nom in QUALIFIE.findall(_texte(fichier)):
                if nom in INTEGREE:
                    continue
                trouvees.setdefault(nom, set()).add(
                    str(fichier.relative_to(RACINE))
                )
    return trouvees


def test_toute_collection_employee_est_declaree() -> None:
    """Le contrôle qui aurait épargné l'enquête de l'issue #50."""
    racines = [RACINE / "labs"]
    if VAULT_PASS.is_file():
        racines.append(RACINE / "solution")

    employees = _employees(racines)
    manquantes = {
        nom: fichiers
        for nom, fichiers in employees.items()
        if nom not in _declarees()
    }

    if manquantes:
        detail = "\n".join(
            f"  {nom} : employée par {min(f)}"
            + (f" et {len(f) - 1} autre(s)" if len(f) > 1 else "")
            for nom, f in sorted(manquantes.items())
        )
        pytest.fail(
            "Ces collections sont employées mais absentes de requirements.yml :\n"
            f"{detail}\n"
            "Sur une machine qui ne les a pas, l'échec se présentera comme un "
            "rc=4 « unreachable », pas comme une dépendance manquante."
        )


def test_le_controle_voit_les_solutions_chiffrees() -> None:
    """Garde-fou du garde-fou : sans lecture des solutions, il ne prouve rien.

    `community.crypto` n'est employée que dans une solution chiffrée. Si le
    déchiffrement échoue en silence, le test précédent passerait au vert sans
    avoir rien regardé : la panne du harnais déguisée en succès.
    """
    if not VAULT_PASS.is_file():
        pytest.skip(".vault-pass absent : les solutions ne sont pas lisibles ici.")

    employees = _employees([RACINE / "solution"])
    assert employees, (
        "Aucune collection trouvée dans solution/ : le déchiffrement a "
        "probablement échoué, et le contrôle ne mesure plus rien."
    )
