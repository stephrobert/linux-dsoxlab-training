"""Vérifie que les liens relatifs des Markdown pointent vers un fichier existant.

Pendant local de `test_doc_urls.py` : celui-ci vérifie les guides en ligne,
celui-là les renvois internes au dépôt. Aucun réseau, donc rapide et
déterministe.

Un lien interne cassé ne fait échouer aucun test fonctionnel : il ne casse que
la navigation de l'apprenant, silencieusement. C'est exactement le genre de
dérive qu'un test attrape mieux qu'une relecture, et le dépôt Ansible jumeau en
a relevé 150 d'un coup le jour où le test y a été écrit : 112 renvois pointaient
un niveau trop haut (`../../README.md` depuis `labs/<section>/<lab>/`, qui vise
un `labs/README.md` inexistant) et 38 gardaient une ancienne numérotation de
répertoires.

Périmètre : tous les `.md` sous `labs/` (README, scénarios, indices, versions
`.fr`) **et** les Markdown de la racine. La racine est incluse ici alors que le
dépôt Ansible s'en tenait à `labs/`, parce que le README racine de ce dépôt est
généré depuis le catalogue (`scripts/gen_catalog.py`) et renvoie donc vers les
répertoires de labs : un lab renommé y laisserait un renvoi mort sans que rien
ne le dise.

Les URL absolues ne sont pas du ressort de ce module : voir `test_doc_urls.py`.

**Ce module n'est pas collecté par la suite normale** : `testpaths = ["labs"]`
dans `pyproject.toml` limite la collecte aux challenges. Il est en revanche
câblé en `pre-commit` (hook `internal-links`), parce qu'il est instantané et
n'a besoin ni de réseau ni de VM. Lancement manuel :

    pytest tests/test_liens_internes.py -v
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.resolve()
LABS = REPO_ROOT / "labs"

# [libellé](cible) où cible est relatif (commence par ./ ou ../).
# Les URL absolues sont du ressort de test_doc_urls.py.
LIEN_RELATIF = re.compile(r"\[[^\]]*\]\((\.\.?/[^)]+)\)")


def _fichiers_markdown() -> list[Path]:
    """Les Markdown des labs, plus ceux de la racine du dépôt."""
    return sorted(LABS.rglob("*.md")) + sorted(REPO_ROOT.glob("*.md"))


def _liens_casses(fichier: Path) -> list[str]:
    """Cibles relatives introuvables depuis ce fichier.

    L'ancre (`#section`) est retirée avant de tester le chemin : elle est
    résolue par le lecteur Markdown, pas par le système de fichiers.
    """
    contenu = fichier.read_text(encoding="utf-8", errors="ignore")
    casses = []
    for cible in LIEN_RELATIF.findall(contenu):
        chemin = (fichier.parent / cible.split("#")[0]).resolve()
        if not chemin.exists():
            casses.append(cible)
    return casses


def test_il_y_a_des_markdown_a_verifier() -> None:
    """Garde-fou : sans lui, un glob cassé rendrait la suite verte à vide."""
    assert _fichiers_markdown(), "aucun .md trouvé sous labs/ : le parcours est cassé"


@pytest.mark.parametrize(
    "fichier",
    _fichiers_markdown(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
)
def test_les_liens_relatifs_pointent_vers_un_fichier_existant(fichier: Path) -> None:
    casses = _liens_casses(fichier)

    assert not casses, (
        f"{fichier.relative_to(REPO_ROOT)} contient {len(casses)} lien(s) mort(s) :\n"
        + "\n".join(f"  - {c}" for c in casses)
        + "\n\nUn renvoi vers un autre lab utilise son chemin réel depuis "
        "`labs/` (`../../<section>/<lab>/`). Depuis un lab, le README racine "
        "est à quatre niveaux : `../../../../README.md`, puisque l'arborescence "
        "est `labs/<categorie>/<section>/<lab>/`."
    )
