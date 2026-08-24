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


def _est_efface(cleanup: str, marqueur: str) -> bool:
    """Le cleanup EFFACE-t-il réellement ce marqueur ?

    Le mentionner ne suffit pas : « . /root/xxx.env » le lit sans le rendre, et
    un commentaire qui le cite satisfaisait la vérification. C'est exactement le
    piège que la partie « comptes » de ce module avait déjà corrigé avec
    `_est_supprime()`, dont la docstring note : « ce test a commencé sa vie
    ainsi, et il passait sur un cleanup dont on venait de retirer le userdel ».
    La leçon n'avait pas été reportée ici.

    Deux formes légitimes, et seulement elles :

    - shell : ``rm`` suivi du chemin, éventuellement parmi d'autres ;
    - Ansible : une tâche qui porte à la fois le chemin et ``state: absent``.
    """
    echappe = re.escape(marqueur)
    # `rm -f a b c` : le marqueur peut être n'importe lequel des chemins.
    if re.search(rf"^\s*rm\b[^\n#]*\s{echappe}(\s|$)", cleanup, re.MULTILINE):
        return True
    # Une tâche Ansible se délimite au « - name: » suivant.
    for tache in re.split(r"\n\s*- name:", cleanup):
        if "state: absent" in tache and re.search(rf"{echappe}(\s|$|\")", tache):
            return True
    return False


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
    assert _est_efface(texte, marqueur), (
        f"{lab.name} : le setup se garde avec « creates: {marqueur} », mais le "
        f"cleanup ne l'EFFACE jamais.\n"
        f"Le mentionner ne suffit pas — « . {marqueur} » le lit, un commentaire "
        f"le cite — et cette vérification a d'ailleurs commencé sa vie ainsi.\n"
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


# ── comptes créés par la SOLUTION ─────────────────────────────────────────────
#
# La solution est chiffrée, donc illisible par un test. Mais les tests du lab,
# eux, nomment forcément les comptes qu'ils attendent : c'est leur objet.
#
# Le cas qui a coûté le plus cher : `rhcsa-mock-exam` fait créer `appuser` avec
# l'UID 1500 par sa solution, et son cleanup échouait à le supprimer. Cinquante
# labs plus loin, `l2-user-lifecycle` créait `alice` avec ce même UID et
# tombait sur « useradd: UID 1500 is not unique ». Le lab accusé n'était pas le
# lab fautif, et il passait parfaitement joué seul.

def _est_supprime(cleanup: str, nom: str) -> bool:
    """Le cleanup SUPPRIME-t-il réellement ce compte ou ce groupe ?

    Chercher le nom n'importe où ne suffit pas : un commentaire qui le cite,
    ou un `pkill -u <nom>` qui ne fait que tuer ses processus, satisfaisaient
    la vérification sans rien supprimer. Ce test a d'ailleurs commencé sa vie
    ainsi, et il passait sur un cleanup dont on venait de retirer le
    `userdel`.

    On exige donc une vraie commande de suppression :

    - `userdel …  <nom>` / `groupdel … <nom>` (shell) ;
    - ou un module Ansible `name: <nom>` suivi de `state: absent`.
    """
    echappe = re.escape(nom)
    if re.search(rf"^\s*(?:user|group)del[^\n#]*\b{echappe}\b", cleanup, re.MULTILINE):
        return True

    # Forme Ansible. On découpe en tâches, et on accepte celle qui porte à la
    # fois `state: absent` et le nom. Cela couvre le `name: alice` direct comme
    # la boucle `name: "{{ item }}"` + `loop:` dont les entrées listent les
    # comptes : c'est la forme qu'emploie `drill-users-groups`, et un motif
    # calé sur `name: <nom>` la déclarait fautive à tort.
    for tache in re.split(r"\n\s*- name:", cleanup):
        if "state: absent" in tache and re.search(rf"\b{echappe}\b", tache):
            return True
    return False


#: `<hôte>.user("X")` dans un test : le compte que le lab attend. La fixture
#: ne s'appelle pas toujours `host` : le capstone RHCSA écrit `srv1.user(...)`,
#: et un motif calé sur `host` laissait justement passer `appuser`, le compte
#: qui a causé tout ce diagnostic.
_COMPTE_TESTE = re.compile(r'\b\w+\.user\(\s*"(?P<nom>[a-z][\w-]*)"\s*\)')

COMPTES_TESTES = [
    (lab, nom)
    for lab in _labs_avec_setup()
    for test in [lab / "challenge" / "tests" / "test_functional.py"]
    if test.is_file()
    for nom in sorted(set(_COMPTE_TESTE.findall(test.read_text(encoding="utf-8"))))
    if nom not in SYSTEME
]


@pytest.mark.parametrize(
    ("lab", "nom"),
    COMPTES_TESTES,
    ids=[f"{lab.name}:{nom}" for lab, nom in COMPTES_TESTES],
)
def test_le_cleanup_supprime_les_comptes_attendus(lab: Path, nom: str) -> None:
    """Ce que la solution crée, le cleanup doit le rendre.

    Un compte survivant garde son UID, et le lab qui voudra le même UID
    échouera à sa place, souvent très loin dans la séquence.
    """
    cleanup = lab / "cleanup.yaml"
    assert cleanup.is_file(), f"{lab.name} a un setup.yaml mais pas de cleanup.yaml"

    assert _est_supprime(cleanup.read_text(encoding="utf-8"), nom), (
        f"{lab.name} : les tests attendent le compte « {nom} », que le cleanup "
        f"ne SUPPRIME pas.\n"
        f"S'il est créé par la solution, il survivra au nettoyage et gardera "
        f"son UID pour tous les labs suivants.\n"
        f"Ajouter par exemple :  userdel -rf {nom}"
    )


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
