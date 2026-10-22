"""Le garde-fou qui separe un verdict de ce qu'il mesure, eprouve des deux cotes.

Le hook `verdicts-et-commun-separes` lit l'INDEX git (`git diff --cached`). En
CI, `pre-commit run --all-files` le lance avec un index vide : il rend 0 sans
rien avoir regarde, et la « parite pre-commit » prouverait donc son existence,
pas son comportement. D'ou ce test, qui monte un depot jetable et place
reellement des fichiers dans l'index.

Les deux sens sont eprouves. Un controle qui refuserait tout serait satisfait
par les trois premiers cas, et bloquerait alors tout commit de releve : le
defaut inverse. Un controle qui n'accepterait que le cas evident laisserait
passer ce qu'il doit arreter.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
OUTIL = RACINE / "tests" / "outils" / "verdicts_et_commun_separes.py"


def _git(depot: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(depot), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un depot jetable, jamais celui du catalogue : son index est partage."""
    for relatif in (
        "validation-labs.json",
        "labs/_commun/gitlab.py",
        "scripts/valider-labs.py",
        "labs/gl-01/challenge/tests/test_functional.py",
        "labs/gl-01/setup.yaml",
        "labs/gl-01/cleanup.yaml",
        "labs/gl-01/lab.yaml",
        "labs/gl-01/README.md",
    ):
        chemin = tmp_path / relatif
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text("depart\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "banc@exemple.test")
    _git(tmp_path, "config", "user.name", "Banc")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "etat de depart")
    return tmp_path


def _indexer(depot: Path, *fichiers: str) -> None:
    for relatif in fichiers:
        chemin = depot / relatif
        chemin.write_text(chemin.read_text(encoding="utf-8") + "modifie\n", encoding="utf-8")
        _git(depot, "add", relatif)


def _jouer(depot: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(OUTIL)],
        cwd=depot,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


REFUSES = [
    ("le releve et le commun", ["validation-labs.json", "labs/_commun/gitlab.py"]),
    ("le releve et l'outillage", ["validation-labs.json", "scripts/valider-labs.py"]),
    (
        "le releve et les deux",
        ["validation-labs.json", "labs/_commun/gitlab.py", "scripts/valider-labs.py"],
    ),
    # Ces quatre cas etaient ACCEPTES par la premiere version du hook, qui
    # jugeait legitime de corriger un lab et de reinscrire son verdict d'un
    # seul geste. C'est precisement le cas qu'aucune mesure ne rattrape apres
    # un squash : le commit unique porte la correction ET le verdict, et rien
    # ne dit lequel est venu avant.
    (
        "le releve et le test d'un lab",
        ["validation-labs.json", "labs/gl-01/challenge/tests/test_functional.py"],
    ),
    ("le releve et un setup", ["validation-labs.json", "labs/gl-01/setup.yaml"]),
    ("le releve et un cleanup", ["validation-labs.json", "labs/gl-01/cleanup.yaml"]),
    ("le releve et un lab.yaml", ["validation-labs.json", "labs/gl-01/lab.yaml"]),
]

ACCEPTES = [
    ("le releve seul", ["validation-labs.json"]),
    ("le commun seul", ["labs/_commun/gitlab.py"]),
    ("l'outillage seul", ["scripts/valider-labs.py"]),
    ("le test d'un lab seul", ["labs/gl-01/challenge/tests/test_functional.py"]),
    # L'enonce n'est pas joue par le cycle : l'interdire obligerait a une
    # campagne pour une coquille d'orthographe, et un garde-fou qui refuse
    # aussi les commits legitimes se contourne au bout de deux jours.
    ("le releve et un enonce", ["validation-labs.json", "labs/gl-01/README.md"]),
    ("rien du tout", []),
]


@pytest.mark.parametrize(("titre", "fichiers"), REFUSES, ids=[t for t, _ in REFUSES])
def test_un_releve_avec_ce_qu_il_mesure_est_refuse(
    depot: Path, titre: str, fichiers: list[str]
) -> None:
    _indexer(depot, *fichiers)
    issue = _jouer(depot)
    assert issue.returncode == 1, (
        f"« {titre} » doit etre refuse : un verdict ecrit dans le meme commit "
        "que le code partage qu'il mesure n'est verifiable par personne, le "
        "controle de peremption comparant des dates de commit."
    )
    assert "REFUS" in issue.stderr
    for relatif in fichiers:
        if relatif != "validation-labs.json":
            assert relatif in issue.stderr, "le message doit NOMMER le fichier fautif"


@pytest.mark.parametrize(("titre", "fichiers"), ACCEPTES, ids=[t for t, _ in ACCEPTES])
def test_ce_qui_est_legitime_passe(depot: Path, titre: str, fichiers: list[str]) -> None:
    _indexer(depot, *fichiers)
    issue = _jouer(depot)
    assert issue.returncode == 0, (
        f"« {titre} » doit passer. Un garde-fou qui refuse aussi les commits "
        "legitimes se contourne au bout de deux jours, et ne controle alors "
        f"plus rien.\n{issue.stderr}"
    )


def test_le_message_donne_le_geste_de_reprise(depot: Path) -> None:
    """Un refus qui ne dit pas quoi faire se contourne par --no-verify."""
    _indexer(depot, "validation-labs.json", "labs/_commun/gitlab.py")
    issue = _jouer(depot)
    assert "git reset HEAD validation-labs.json" in issue.stderr
    assert "valider-labs.py" in issue.stderr
