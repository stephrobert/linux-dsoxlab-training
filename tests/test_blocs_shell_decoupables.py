"""Tout bloc `shell` d'un setup ou d'un cleanup doit survivre au découpage
d'arguments qu'Ansible lui fait subir.

POURQUOI CE MODULE EXISTE.

Le 2026-09-16, trois labs sont devenus injouables d'un coup, avec un message
qui ne désignait rien :

    setup.yaml a échoué (rc=4, status=failed). Stats : {}

La cause tenait à une apostrophe. Le module `shell` d'Ansible s'emploie en
FORME LIBRE : avant d'exécuter quoi que ce soit, Ansible découpe le contenu
avec `shlex` pour y chercher des paires clé=valeur comme `chdir=` ou
`creates=`. Un guillemet simple non apparié fait échouer ce découpage, et le
playbook ne démarre jamais.

Or le français est plein d'apostrophes. Un commentaire ajouté dans un bloc
shell, « qui n'a de sens que pour... », suffit à casser le lab. Pire : cela ne
casse que si le nombre total d'apostrophes du bloc devient IMPAIR. Les labs
touchés avaient vécu des mois avec un commentaire contenant « S'assurer »,
parce qu'un second guillemet ailleurs rétablissait la parité par hasard.

Un défaut qui dépend d'une parité accidentelle ne se voit pas à la relecture.
Ce test le voit, et il nomme la ligne fautive.

La correction, quand ce test échoue : réécrire le commentaire sans apostrophe,
ou passer la tâche en forme explicite `ansible.builtin.shell: {cmd: ...}`, qui
n'est pas soumise au découpage.

Ce module n'est pas collecté par la suite des labs : `testpaths` limite la
collecte aux challenges. Lancement :

    pytest tests/test_blocs_shell_decoupables.py -v
"""

from __future__ import annotations

import shlex
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parent.parent
LABS = RACINE / "labs"

#: Les modules employés en forme libre, donc soumis au découpage d'Ansible.
#: `command` l'est aussi, et pour la même raison.
MODULES = ("ansible.builtin.shell", "ansible.builtin.command", "shell", "command")

PLAYBOOKS = sorted(
    list(LABS.rglob("setup.yaml"))
    + list(LABS.rglob("cleanup.yaml"))
    + list((RACINE / "shared").rglob("*.yml"))
)


def _blocs(playbook: Path):
    """Chaque bloc de forme libre du playbook, avec le nom de sa tâche."""
    try:
        contenu = yaml.safe_load(playbook.read_text(encoding="utf-8"))
    except yaml.YAMLError as erreur:
        pytest.fail(f"{playbook.relative_to(RACINE)} n'est pas un YAML lisible : {erreur}")
    if not contenu:
        return
    plays = contenu if isinstance(contenu, list) else [contenu]
    for play in plays:
        if not isinstance(play, dict):
            continue
        # Un fichier de tâches incluses n'a pas de clé `tasks` : il EST la liste.
        taches = play.get("tasks") if "tasks" in play else [play]
        for tache in taches or []:
            if not isinstance(tache, dict):
                continue
            for module in MODULES:
                valeur = tache.get(module)
                if isinstance(valeur, str):
                    yield tache.get("name", "(sans nom)"), valeur


def test_il_y_a_des_playbooks_a_controler() -> None:
    """Garde-fou : un parcours cassé rendrait la suite verte à vide."""
    assert len(PLAYBOOKS) > 50, (
        f"Seulement {len(PLAYBOOKS)} playbook(s) trouvé(s) : le parcours est "
        "cassé, et le contrôle ne mesure plus rien."
    )


@pytest.mark.parametrize(
    "playbook", PLAYBOOKS, ids=lambda p: str(p.relative_to(RACINE))
)
def test_les_blocs_survivent_au_decoupage_d_arguments(playbook: Path) -> None:
    fautifs = []
    for nom, bloc in _blocs(playbook):
        try:
            shlex.split(bloc)
        except ValueError as erreur:
            lignes_fautives = []
            for numero, ligne in enumerate(bloc.splitlines(), 1):
                try:
                    shlex.split(ligne)
                except ValueError:
                    lignes_fautives.append(f"ligne {numero} : {ligne.strip()}")
            fautifs.append(
                f"tâche « {nom} » : {erreur}\n      "
                + "\n      ".join(lignes_fautives or ["(guillemet réparti sur plusieurs lignes)"])
            )

    assert not fautifs, (
        f"{playbook.relative_to(RACINE)} porte un bloc qu'Ansible ne saura pas "
        "découper :\n    " + "\n    ".join(fautifs) + "\n\n"
        "Le module shell s'emploie en forme libre : Ansible découpe le contenu "
        "avec shlex pour y chercher chdir= ou creates=, et un guillemet simple "
        "non apparié fait échouer ce découpage AVANT toute exécution. Le "
        "playbook rend alors « rc=4, status=failed » sans rien désigner.\n\n"
        "Réécrivez le commentaire sans apostrophe, ou passez la tâche en forme "
        "explicite avec cmd:, qui n'est pas découpée."
    )
