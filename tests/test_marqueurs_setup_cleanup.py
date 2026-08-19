"""Tout marqueur qui garde un `setup.yaml` doit être effacé par son `cleanup.yaml`.

Incident à l'origine de ce module. `l2-filesystem-create-xfs` prépare sa
partition dans une tâche gardée par `args: creates: /root/.xfs-lab-ready`. Son
`cleanup.yaml` effaçait le système de fichiers mais **pas le marqueur**. Après
un nettoyage, le disque était vierge et le marqueur toujours là : au `setup`
suivant, Ansible sautait la tâche « déjà faite », la partition n'était jamais
recréée, et la solution de référence échouait sur une partition inexistante.

Le lab n'était donc plus rejouable, et rien ne le signalait : ni le validator,
ni les tests du lab, qui ne tournent que sur un lab déjà préparé.

La règle est simple et vérifiable sans VM, par simple lecture des deux
playbooks : ce qu'un `creates:` protège, un `cleanup` doit le rendre. Sinon le
lab ne se réinitialise qu'une fois.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

#: `args: creates: <chemin>` — la garde d'idempotence d'Ansible.
_CREATES = re.compile(r"^\s*creates:\s*(?P<chemin>\S+)\s*$", re.MULTILINE)

#: Marqueurs volontairement conservés, avec le motif. Une exemption se discute
#: en revue ; elle ne se contourne pas en supprimant le test. Le motif doit
#: expliquer pourquoi le lab reste rejouable **malgré** le marqueur conservé.
EXEMPTIONS: dict[tuple[str, str], str] = {
    ("l4-ldap-integration", "/etc/dirsrv/slapd-lab"): (
        "L'instance 389-ds est délibérément conservée entre deux passages : "
        "elle est longue à créer et son cleanup ne vise que le client. Le lab "
        "reste rejouable parce que le setup réutilise l'annuaire en place au "
        "lieu de le recréer."
    ),
}


def _labs_avec_setup() -> list[Path]:
    return sorted(p.parent for p in (REPO / "labs").rglob("setup.yaml"))


def _marqueurs(setup: Path) -> list[str]:
    return _CREATES.findall(setup.read_text(encoding="utf-8"))


CAS = [
    (lab, marqueur)
    for lab in _labs_avec_setup()
    for marqueur in _marqueurs(lab / "setup.yaml")
]


@pytest.mark.parametrize(
    ("lab", "marqueur"),
    CAS,
    ids=[f"{lab.name}:{marqueur}" for lab, marqueur in CAS],
)
def test_le_cleanup_efface_le_marqueur(lab: Path, marqueur: str) -> None:
    """Sans cela, le lab ne se réinitialise qu'une seule fois."""
    motif = EXEMPTIONS.get((lab.name, marqueur))
    if motif:
        pytest.skip(f"exemption assumée : {motif}")

    cleanup = lab / "cleanup.yaml"
    assert cleanup.is_file(), f"{lab.name} a un setup.yaml mais pas de cleanup.yaml"

    texte = cleanup.read_text(encoding="utf-8")
    assert marqueur in texte, (
        f"{lab.name} : le setup se garde avec « creates: {marqueur} », mais le "
        f"cleanup ne mentionne jamais ce chemin.\n"
        f"Le nettoyage laissera donc le marqueur en place : au prochain setup, "
        f"la tâche sera sautée et l'état de départ ne sera jamais reconstruit.\n"
        f"Ajouter par exemple :  rm -f {marqueur}"
    )


def test_il_y_a_bien_des_marqueurs_a_verifier() -> None:
    """Une liste vide ferait passer ce module pour rien."""
    assert len(CAS) >= 5, (
        f"seulement {len(CAS)} garde(s) « creates: » trouvée(s) : la détection "
        "est cassée, pas le catalogue"
    )


# ── comptes créés par un setup ────────────────────────────────────────────────
#
# Même règle, autre ressource. `l2-collaborative-setgid` créait alice, bob et
# devteam sans jamais les supprimer : `l2-user-lifecycle`, qui passe après dans
# la séquence et dont la solution fait un `useradd alice`, échouait sur un
# compte déjà pris. Le lab fautif, lui, restait vert.

#: `ansible.builtin.user: name: X` / `group: name: X` dans un setup.
_COMPTE = re.compile(
    r"ansible\.builtin\.(?P<genre>user|group):\s*\n\s*name:\s*(?P<nom>[a-z][\w-]*)",
    re.MULTILINE,
)

#: Comptes fournis par l'image ou par dsoxlab, qu'un lab ne doit pas supprimer.
SYSTEME = {"root", "ansible", "student", "nobody", "wheel", "sudo", "adm"}

COMPTES = [
    (lab, m.group("genre"), m.group("nom"))
    for lab in _labs_avec_setup()
    for m in _COMPTE.finditer((lab / "setup.yaml").read_text(encoding="utf-8"))
    if m.group("nom") not in SYSTEME
]


@pytest.mark.parametrize(
    ("lab", "genre", "nom"),
    COMPTES,
    ids=[f"{lab.name}:{genre}:{nom}" for lab, genre, nom in COMPTES],
)
def test_le_cleanup_supprime_les_comptes_crees(lab: Path, genre: str, nom: str) -> None:
    """Un compte laissé derrière soi fait échouer le lab suivant, pas celui-ci."""
    cleanup = lab / "cleanup.yaml"
    assert cleanup.is_file(), f"{lab.name} a un setup.yaml mais pas de cleanup.yaml"

    assert nom in cleanup.read_text(encoding="utf-8"), (
        f"{lab.name} : le setup crée le {genre} « {nom} », que le cleanup ne "
        f"mentionne jamais.\n"
        f"Le compte survivra au nettoyage et occupera son nom (et son UID/GID) "
        f"pour tous les labs suivants.\n"
        f"Ajouter par exemple :  {'userdel -r' if genre == 'user' else 'groupdel'} {nom}"
    )
