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
contrat dsoxlab, et il est instantané (aucun réseau, aucune VM, une lecture
d'en-tête par solution).

Le module porte DEUX contrôles, et le second est né d'un défaut réel constaté
le 2026-09-15. Les capstones `capstone-serveur-casse` et
`capstone-mise-en-production` ont été commités, leurs solutions écrites, mais
jamais ajoutées à git : elles sont restées **en clair et non suivies** sur le
disque de l'auteur. Le premier contrôle ne pouvait rien voir, puisqu'il ne
regarde que ce que git suit ; et quiconque clonait le dépôt obtenait deux
capstones sans solution, donc invérifiables par `verify-solutions.py`.

Une solution doit donc être **suivie** autant que **chiffrée**, et l'oubli de
l'une est aussi silencieux que l'oubli de l'autre.

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

# Rien à chiffrer dans ces fichiers de service. `verified-with.json` est le
# verdict écrit par `scripts/verify-solutions.py` : il dit quelle solution a
# été rejouée avec quel interpréteur et quand, sans jamais citer son contenu.
EXEMPTS = {".gitkeep", ".gitignore", "verified-with.json"}


def _fichiers_suivis() -> list[Path]:
    """Fichiers de `solution/` que git suit réellement.

    Ce premier contrôle ne porte que sur eux, et c'est `git ls-files` qui
    tranche : un fichier tout juste ajouté à l'index y figure déjà, donc le
    hook pre-commit le voit avant qu'il ne parte.

    Ce que cette liste ne voit PAS, c'est une solution restée hors de git.
    C'est le rôle du second contrôle, plus bas, et il a fallu deux capstones
    livrés sans leur solution pour s'en apercevoir.
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


def _fichiers_sur_disque() -> list[Path]:
    """Tout ce qui vit sous `solution/`, que git le connaisse ou non."""
    if not SOLUTION_DIR.is_dir():
        return []
    return sorted(
        p
        for p in SOLUTION_DIR.rglob("*")
        if p.is_file() and p.name not in EXEMPTS and p.stat().st_size > 0
    )


def test_aucune_solution_n_echappe_a_git() -> None:
    """Une solution hors de git est invisible pour le contrôle précédent.

    Deux conséquences, et la seconde est la plus coûteuse :

    - elle reste en clair sur le disque sans que rien ne le signale, puisque
      le premier contrôle ne lit que ce que git suit ;
    - surtout, **elle n'existe pas pour qui clone le dépôt**. Le lab est
      publié, son README annonce une solution du formateur, et
      `scripts/verify-solutions.py` ne peut pas prouver qu'il est faisable.

    Mesuré le 2026-09-15 : les deux capstones étaient dans ce cas depuis leur
    commit, et c'est une relecture humaine qui l'a vu, pas l'outillage.
    """
    suivis = {
        (REPO_ROOT / rel.decode()).resolve()
        for rel in subprocess.run(
            ["git", "ls-files", "-z", "--", "solution"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        ).stdout.split(b"\0")
        if rel
    }
    oubliees = [p for p in _fichiers_sur_disque() if p.resolve() not in suivis]

    assert not oubliees, (
        "solution(s) présente(s) sur le disque mais absente(s) de git :\n"
        + "\n".join(f"  {p.relative_to(REPO_ROOT)}" for p in oubliees)
        + "\n\nUn clone du dépôt n'aurait pas ces solutions, et le lab "
        "correspondant serait invérifiable. Chiffrez-les, puis ajoutez-les :\n"
        "  ansible-vault encrypt --vault-password-file .vault-pass <fichier>\n"
        "  git add <fichier>"
    )
