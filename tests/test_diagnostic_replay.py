"""Un replay de solution en échec doit dire POURQUOI il a échoué.

Incident à l'origine de ce module. Le replay de `rhcsa-mock-exam` échouait par
intermittence, et le message se résumait à :

    solution.yaml a échoué pour rhcsa-mock-exam (rc=2, status=failed).
    Stats : {'ok': {...}, 'failures': {'alma-rhcsa-1.lab': 1}}

Ni la tâche fautive, ni sa raison. Reproduire coûte une passe entière sur
l'infrastructure, et l'issue est restée ouverte des semaines faute de matière.

On a longtemps cru la sortie perdue, `run_playbook` créant un répertoire
temporaire qu'il nettoie ensuite. C'est inexact : `dsoxlab` lit le stdout avant
de supprimer ce répertoire. Vérifié en jouant un vrai playbook en échec dans
les conditions exactes du conftest (`quiet=True`, `private_data_dir=None`) :
1522 caractères, avec la tâche fautive, le `fatal:` et le `PLAY RECAP`.

L'information était donc là, et c'est le conftest qui la jetait.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parent.parent


def _charger_conftest() -> Any:
    """Charge le conftest racine comme module, pour en tester une fonction.

    Passer par importlib plutôt que par un `import conftest` : ce dernier
    dépend du mode d'import de pytest et du répertoire courant, deux choses qui
    varient selon qu'on lance la suite depuis la racine ou depuis `tests/`.
    """
    chemin = REPO / "conftest.py"
    spec = importlib.util.spec_from_file_location("conftest_racine", chemin)
    assert spec and spec.loader, f"conftest illisible : {chemin}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["conftest_racine"] = module
    spec.loader.exec_module(module)
    return module


@dataclass
class ResultatFactice:
    """Ce que `dsoxlab.infra.ansible.run_playbook` rend, réduit à l'utile."""

    rc: int
    status: str
    stats: dict[str, dict[str, int]]
    stdout: str


#: Une sortie d'échec réaliste, calquée sur ce qu'ansible-runner produit
#: réellement (mesuré, cf. docstring du module).
SORTIE = (
    "TASK [Creer le volume logique] *************************************\n"
    'fatal: [alma-rhcsa-1.lab]: FAILED! => {"msg": "Volume group vgapp not found"}\n'
    "\n"
    "PLAY RECAP *********************************************************\n"
    "alma-rhcsa-1.lab  : ok=2  changed=1  unreachable=0  failed=1\n"
)


@pytest.fixture(scope="module")
def message() -> Any:
    return _charger_conftest().message_echec_solution


def test_la_tache_fautive_et_sa_raison_apparaissent(message: Any) -> None:
    """Le cœur du correctif : on doit pouvoir diagnostiquer sans rejouer."""
    texte = message(
        "rhcsa-mock-exam",
        ResultatFactice(
            rc=2,
            status="failed",
            stats={"failures": {"alma-rhcsa-1.lab": 1}},
            stdout=SORTIE,
        ),
    )
    assert "Creer le volume logique" in texte, "la tâche fautive doit être nommée"
    assert "Volume group vgapp not found" in texte, "la raison doit être donnée"


def test_le_message_garde_ce_qu_il_disait_deja(message: Any) -> None:
    """Le correctif ajoute, il ne remplace pas : rc, status et stats restent."""
    texte = message(
        "rhcsa-mock-exam",
        ResultatFactice(rc=2, status="failed", stats={"ok": {"h": 4}}, stdout=SORTIE),
    )
    assert "rhcsa-mock-exam" in texte
    assert "rc=2" in texte
    assert "status=failed" in texte
    assert "{'ok': {'h': 4}}" in texte


@pytest.mark.parametrize("vide", ["", "   ", "\n\n  \n"])
def test_sans_sortie_aucune_section_vide(message: Any, vide: str) -> None:
    """Un playbook muet ne doit pas produire un en-tête suivi de rien.

    Une section « Sortie du playbook » vide laisse croire que le playbook n'a
    rien dit, alors que le cas réel est qu'on n'a pas su la lire.
    """
    texte = message(
        "un-lab", ResultatFactice(rc=1, status="failed", stats={}, stdout=vide)
    )
    assert "Sortie du playbook" not in texte
    assert "rc=1" in texte


def test_une_sortie_enorme_est_tronquee(message: Any) -> None:
    """Un playbook verbeux ne doit pas noyer la console de l'utilisateur.

    On garde la FIN : Ansible s'arrête à la tâche fautive, donc l'erreur est
    toujours dans les derniers caractères. Tronquer par le début la perdrait.
    """
    bruit = "ligne de bruit sans intérêt\n" * 2000
    texte = message(
        "un-lab",
        ResultatFactice(
            rc=2, status="failed", stats={}, stdout=bruit + SORTIE
        ),
    )
    assert len(texte) < 6000, "le message doit rester lisible dans un terminal"
    assert "Volume group vgapp not found" in texte, (
        "la fin doit survivre à la troncature, c'est là qu'est l'erreur"
    )


def test_la_fixture_de_replay_utilise_bien_cette_fonction() -> None:
    """Garde-fou : la fonction ne doit pas devenir du code mort.

    Les tests ci-dessus passeraient encore si quelqu'un remettait un message
    en dur dans la fixture. On vérifie donc que c'est bien elle qui est appelée.
    """
    source = (REPO / "conftest.py").read_text(encoding="utf-8")
    assert "raise RuntimeError(message_echec_solution(" in source, (
        "la fixture _apply_lab_state doit lever avec message_echec_solution(), "
        "sinon cette fonction est testée mais jamais utilisée"
    )
