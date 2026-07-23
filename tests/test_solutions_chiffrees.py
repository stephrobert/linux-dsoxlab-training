"""Vérifie qu'aucune solution de formateur n'est en clair dans `solution/`.

Une solution en clair spoile le lab, et l'historique git la conserve : une fois
poussée, la retirer ne suffit plus. Le contrôle mérite donc d'être mécanique.

Le risque n'est pas théorique : corriger une solution impose de la déchiffrer,
puis de la re-chiffrer. Un `ansible-vault encrypt` oublié en fin de manipulation
laisse la réponse lisible dans le dépôt, sans que rien ne le signale. Le
`conftest.py` racine déchiffre d'ailleurs ces fichiers **en mémoire** pour
rejouer la solution avant les tests, justement pour ne jamais avoir à les poser
en clair sur disque : ce test est le garde-fou de cette discipline.

Périmètre réel du dépôt Linux : 84 solutions sous
`solution/linux/<section>/<lab>/`, en deux formes selon le runtime du lab :

- `solution.yaml` pour les labs `runtime: vm` (playbook rejoué par ansible-runner) ;
- `solution.sh` pour les labs `runtime: shell` (script bash joué dans le workdir).

Le test ne distingue pas les deux : il contrôle l'en-tête de chiffrement de
**tout** fichier suivi par git sous `solution/`, quelle que soit son extension.
C'est volontaire, et plus sûr qu'une liste d'extensions à tenir à jour.

Contrairement au dépôt Ansible jumeau, il n'y a pas de script shell qui double
ce contrôle : ce module **est** le hook `solutions-encrypted` de
`.pre-commit-config.yaml`. C'est cohérent avec le zéro-bash imposé par le
contrat dsoxlab, et il est instantané (aucun réseau, aucune VM, 84 lectures
d'en-tête).

**Ce module n'est pas collecté par la suite normale** : `testpaths = ["labs"]`
dans `pyproject.toml` limite la collecte aux challenges. Lancement manuel :

    pytest tests/test_solutions_chiffrees.py -v
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.resolve()
SOLUTION_DIR = REPO_ROOT / "solution"
VAULT_HEADER = b"$ANSIBLE_VAULT"

# Rien à chiffrer dans ces fichiers de service.
EXEMPTS = {".gitkeep", ".gitignore"}


def _fichiers_suivis() -> list[Path]:
    """Fichiers de `solution/` que git suit réellement.

    Un fichier non suivi ne partira pas dans un commit, donc il ne peut pas
    fuiter. Inclure les non-suivis ferait échouer le test sur des artefacts de
    travail locaux (un déchiffrement en cours, par exemple), ce qui
    n'apporterait rien.
    """
    if not SOLUTION_DIR.is_dir():
        return []
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", "solution"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout
    fichiers = []
    for rel in out.split(b"\0"):
        if not rel:
            continue
        p = REPO_ROOT / rel.decode()
        if p.name in EXEMPTS or not p.is_file():
            continue
        if p.stat().st_size == 0:  # un fichier vide ne révèle rien
            continue
        fichiers.append(p)
    return fichiers


SOLUTIONS = _fichiers_suivis()


def test_le_repertoire_solution_est_bien_peuple() -> None:
    """Garde-fou : sans lui, un `git ls-files` cassé rendrait la suite verte à vide."""
    assert SOLUTIONS, (
        "aucun fichier suivi trouvé sous solution/ : le parcours est cassé, "
        "ou le dépôt n'a pas de solutions (auquel cas ce test n'a pas lieu d'être)"
    )


@pytest.mark.parametrize(
    "fichier",
    SOLUTIONS,
    ids=lambda p: str(p.relative_to(SOLUTION_DIR)),
)
def test_la_solution_est_chiffree(fichier: Path) -> None:
    entete = fichier.read_bytes()[: len(VAULT_HEADER)]

    assert entete == VAULT_HEADER, (
        f"{fichier.relative_to(REPO_ROOT)} n'est PAS chiffré.\n\n"
        "Une solution en clair spoile le lab, et git en garde la trace même après "
        "correction. Rechiffrez avant de committer :\n"
        f"  ansible-vault encrypt --vault-password-file .vault-pass "
        f"{fichier.relative_to(REPO_ROOT)}"
    )
