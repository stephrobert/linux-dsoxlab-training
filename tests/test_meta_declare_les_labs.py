"""Tout lab livré est déclaré dans `meta.yml`, et réciproquement.

POURQUOI CE MODULE EXISTE.

Le 2026-09-17, deux capstones livrés et validés, `capstone-mise-en-production`
et `capstone-serveur-casse`, se sont retrouvés absents de `meta.yml`. Le commit
qui les a ajoutés n'a pas touché ce fichier, et rien ne l'a signalé.

Conséquence : ils existent sur le disque, `dsoxlab validate-structure` les
valide, mais le parcours n'en dit rien. Un apprenant qui suit `meta.yml` ne les
jouera jamais. Du travail livré, invisible.

Rien ne pouvait le voir. `dsoxlab validate-structure` lit les répertoires de
`labs/` et ne sait rien de `meta.yml` ; `gen_catalog.py` rend les deux vues
sans se plaindre qu'elles divergent. Chacun avait raison de son côté, et le
trou était entre les deux.

Le contrôle porte donc sur l'ÉCART entre deux sources, dans les deux sens :

- un lab sur disque mais non déclaré est invisible du parcours ;
- un lab déclaré mais absent du disque casse le parcours.

CE CATALOGUE RANGE SES LABS AUTREMENT que le catalogue Kubernetes, d'où ce
module vient. Ici, un lab vit sous `labs/linux/<section>/<lab>/` et `meta.yml`
le déclare par son chemin relatif à `labs/`, soit `linux/<section>/<lab>`. Là
-bas, un lab vit sous `labs/<lab>/` et se déclare par son seul nom. Confondre
les deux conventions fait apparaître TOUS les labs comme manquants des deux
côtés : c'est arrivé en portant ce contrôle, et le faux positif portait sur 87
labs.

Lancement :

    pytest tests/test_meta_declare_les_labs.py -v
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from lecture_yaml import lire_yaml

META = RACINE / "meta.yml"
LABS = RACINE / "labs"


def _declares() -> list[str]:
    """Les labs que `meta.yml` déclare, dans l'ordre, section par section."""
    donnees = lire_yaml(META)
    declares: list[str] = []
    for section in donnees.get("sections") or []:
        declares += [str(lab) for lab in (section.get("labs") or [])]
    return declares


def _sur_disque() -> set[str]:
    """Les labs réellement livrés, par leur chemin relatif à `labs/`.

    On cherche les `lab.yaml` À TOUTE PROFONDEUR plutôt que d'énumérer un
    niveau fixe : la profondeur est une convention du dépôt, pas une propriété
    d'un lab, et la coder en dur rendrait ce contrôle faux le jour où une
    section gagne un sous-niveau.
    """
    return {
        str(contrat.parent.relative_to(LABS))
        for contrat in LABS.rglob("lab.yaml")
    }


def test_le_parcours_n_est_pas_vide() -> None:
    """Garde-fou : un `meta.yml` aux sections vides rendrait tout le reste
    vert, et ce test-ci avec."""
    declares = _declares()
    assert len(declares) > 50, (
        f"Seulement {len(declares)} lab(s) déclaré(s) dans meta.yml : les "
        "sections sont vides ou le parcours est cassé, et l'apprenant se "
        "retrouve devant un catalogue sans ordre."
    )


def test_chaque_lab_livre_est_declare_dans_le_parcours() -> None:
    oublies = sorted(_sur_disque() - set(_declares()))
    assert not oublies, (
        "Lab(s) livré(s) mais absent(s) du parcours de meta.yml :\n  "
        + "\n  ".join(oublies)
        + "\n\nIls existent sur le disque et `validate-structure` les valide, "
        "mais le parcours n'en dit rien : un apprenant qui suit meta.yml ne "
        "les jouera jamais. Ajoutez-les dans la section de leur bloc, à la "
        "place que leur difficulté justifie."
    )


def test_chaque_lab_declare_existe_vraiment() -> None:
    fantomes = [lab for lab in _declares() if lab not in _sur_disque()]
    assert not fantomes, (
        "Lab(s) déclaré(s) dans meta.yml mais absent(s) de labs/ :\n  "
        + "\n  ".join(fantomes)
        + "\n\nSoit le lab a été renommé sans que meta.yml suive, soit ses "
        "fichiers ont été perdus. Le second cas se voit mal : un répertoire de "
        "lab peut survivre à une manipulation de branches avec son seul "
        "sous-dossier challenge/, ce qui ne se remarque pas dans un `ls`."
    )


def test_aucun_lab_n_est_declare_deux_fois() -> None:
    """Un lab dans deux sections apparaîtrait deux fois dans le parcours, avec
    deux numéros d'ordre différents, ce qui n'a pas de sens."""
    doublons = sorted(lab for lab, n in Counter(_declares()).items() if n > 1)
    assert not doublons, (
        f"Lab(s) déclaré(s) plusieurs fois : {', '.join(doublons)}."
    )


#: Ce qu'un lab de CE catalogue porte forcément.
#:
#: La liste a été MESURÉE sur les 86 labs, et non recopiée de celle du
#: catalogue Kubernetes. La recopier aurait produit un contrôle qui hurle sans
#: rien avoir trouvé, sur trois points :
#:
#:     challenge/solution.sh    0/86   les solutions vivent dans `solution/`,
#:                                     chiffrées par ansible-vault
#:     setup.yaml, cleanup.yaml 66/86  aucun lab `l1` n'en a, et c'est normal :
#:                                     ces labs d'introduction n'ont aucune
#:                                     infrastructure à poser
#:     challenge/hints.yaml     73/86  tous les labs n'offrent pas d'indices
#:
#: Ne figurent donc ici que les fichiers présents dans 86 labs sur 86. Deux
#: d'entre eux n'existent pas dans le catalogue Kubernetes, les README de
#: challenge.
ATTENDUS = (
    "lab.yaml",
    "lab.fr.yaml",
    "scenario.md",
    "scenario.fr.md",
    "README.md",
    "README.fr.md",
    "challenge/README.md",
    "challenge/README.fr.md",
    "challenge/tests/test_functional.py",
)


def test_aucun_repertoire_de_lab_n_est_ampute() -> None:
    """Un répertoire de lab incomplet est INVISIBLE pour le reste de
    l'outillage, et c'est ce qui le rend dangereux.

    Ce test énumère les RÉPERTOIRES qui portent un `challenge/`, pas les
    `lab.yaml` : on ne peut pas constater l'absence d'un `lab.yaml` en partant
    de ce fichier. C'est exactement ainsi qu'un lab amputé passe au travers de
    `validate-structure`, qui énumère les labs par leur contrat.
    """
    incomplets = {}
    for challenge in sorted(LABS.rglob("challenge")):
        if not challenge.is_dir():
            continue
        lab = challenge.parent
        manquants = [f for f in ATTENDUS if not (lab / f).is_file()]
        if manquants:
            incomplets[str(lab.relative_to(LABS))] = manquants

    assert not incomplets, (
        "Répertoire(s) de lab incomplet(s) :\n"
        + "\n".join(
            f"  {lab} : il manque {', '.join(fichiers)}"
            for lab, fichiers in incomplets.items()
        )
        + "\n\nUn lab privé de son `lab.yaml` n'existe plus pour "
        "`validate-structure` ni pour `gen_catalog.py`, qui énumèrent les labs "
        "par ce fichier. Il disparaît du catalogue sans qu'un seul contrôle ne "
        "bronche."
    )
