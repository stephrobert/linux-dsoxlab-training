"""Tout `setup.yaml` / `cleanup.yaml` doit être chargeable par Ansible.

Incident à l'origine de ce module. Un commentaire français ajouté **dans** un
bloc `ansible.builtin.shell` a suffi à casser un playbook : l'apostrophe de
« n'empêche » déséquilibre le découpage des arguments, et Ansible refuse de
charger la tâche avec « failed at splitting arguments, either an unbalanced
jinja2 block or quotes ».

Le fichier restait un YAML parfaitement valide. `yaml.safe_load` passait,
`dsoxlab validate-structure` passait, et le défaut ne se voyait qu'à
l'exécution, sous la forme d'un `dsoxlab reset` qui échouait en `rc=4` sans
jouer une seule tâche. Autrement dit : vérifier la forme ne prouve pas que ça
s'exécute, seul `--syntax-check` charge réellement les tâches.

Un commentaire explicatif se met donc **au-dessus** de la tâche, en YAML, pas
à l'intérieur du bloc shell.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PLAYBOOKS = sorted(
    p for p in (REPO / "labs").rglob("*.yaml")
    if p.name in {"setup.yaml", "cleanup.yaml"}
)

ANSIBLE = shutil.which("ansible-playbook")


@pytest.mark.skipif(ANSIBLE is None, reason="ansible-playbook absent du PATH")
@pytest.mark.parametrize("playbook", PLAYBOOKS, ids=lambda p: str(p.relative_to(REPO)))
def test_le_playbook_se_charge(playbook: Path) -> None:
    """`--syntax-check` charge les tâches, là où un parseur YAML ne fait que lire."""
    assert ANSIBLE is not None
    resultat = subprocess.run(
        [ANSIBLE, "--syntax-check", "-i", "localhost,", str(playbook)],
        capture_output=True,
        text=True,
        cwd=REPO,
        # C'est le code de retour qu'on veut juger, pas une exception : un
        # playbook qui ne se charge pas doit produire un échec de test lisible.
        check=False,
    )

    assert resultat.returncode == 0, (
        f"{playbook.relative_to(REPO)} ne se charge pas :\n"
        f"{resultat.stdout.strip()}\n{resultat.stderr.strip()}"
    )


def test_le_catalogue_a_bien_des_playbooks() -> None:
    """Garde-fou du garde-fou : une liste vide ferait passer le test pour rien."""
    assert len(PLAYBOOKS) > 100, (
        f"seulement {len(PLAYBOOKS)} playbook(s) découvert(s) : la découverte "
        "est cassée, pas le catalogue"
    )
