#!/usr/bin/env python3
"""Un verdict ne se commite pas avec ce qu'il mesure.

POURQUOI CE GARDE-FOU EXISTE

Le 2026-10-22, une correction de `labs/_commun/` et les verdicts qu'elle
rendait caducs sont partis dans le MEME commit. Le defaut est passe inapercu
plusieurs heures, et pas par inattention : le generateur du registre, cote
site, classe un lab « a reattester » quand un commit POSTERIEUR a son verdict
touche ses fichiers. Verdicts et modification du commun etant dans le meme
commit, aucun verdict n'etait posterieur a quoi que ce soit, et le controle
concluait que tout allait bien.

La correction elle-meme etait juste : elargir le patch du registre local a
tous les fichiers de pipeline. Mais elle employait `ansible.builtin.find`, qui
IGNORE LES FICHIERS CACHES par defaut, et `.gitlab-ci.yml` commence par un
point. Elle a donc repare les labs dont le service vit dans `ci/*.yml` et
casse en silence tous ceux dont le service vit a la racine. Vingt et un
verdicts VALIDE ne valaient plus rien, et rien ne le disait.

CE QUE CE CONTROLE IMPOSE

L'ordre, et qu'il soit VISIBLE dans l'historique :

    1. le correctif du commun, dans son commit ;
    2. la campagne de validation ;
    3. le releve, dans un commit qui ne change rien d'autre.

Un verdict n'est lisible que s'il est ecrit par un commit qui ne modifie pas ce
qu'il mesure. Autrement, « ce verdict est-il encore valable ? » n'a plus de
reponse mecanique, et il faut croire l'auteur sur parole.

CE QU'IL NE PEUT PAS FAIRE

Il ne verifie pas que la campagne a REELLEMENT tourne entre les deux commits :
rien dans un depot git ne le prouve. Il rend seulement la question posable.
"""

from __future__ import annotations

import subprocess
import sys

# Ce qu'un verdict MESURE, et qui ne doit donc pas bouger dans le commit qui
# l'inscrit.
#
# La premiere version n'interdisait que le COMMUN et l'outillage, en jugeant
# legitime qu'un commit corrige UN lab et reinscrive SON verdict. C'etait une
# erreur, et elle laissait ouvert exactement le cas qu'aucune mesure ne peut
# rattraper ensuite : si une pull request squashee retouche un test APRES sa
# campagne, le commit unique porte les deux, et le squash a DETRUIT
# l'information qui les distinguait. Ni une date, ni un diff entre deux
# arbres, ni rien d'autre ne peut plus dire lequel est venu avant.
#
# Un controle ne peut donc pas constater cette faute apres coup. Il reste a
# l'empecher, ce que fait ce hook : le releve se commite SEUL, apres la
# campagne qui l'a produit.
#
# Ce qui est mesure, c'est ce que le cycle JOUE. L'enonce, le scenario et les
# indices n'en font pas partie : ils ne sont pas executes, et les interdire
# obligerait a une campagne pour une coquille d'orthographe.
MESURE = (
    "labs/_commun/",  # porte tous les labs a la fois
    "scripts/",  # l'outillage qui produit le verdict
)
# Les fichiers d'un lab que le cycle joue, reconnus par leur fin de chemin.
MESURE_PAR_LAB = (
    "/lab.yaml",
    "/setup.yaml",
    "/cleanup.yaml",
)
TESTS_DU_LAB = "/challenge/tests/"
RELEVE = "validation-labs.json"


def mesure_un_verdict(chemin: str) -> bool:
    """Vrai si ce fichier determine ce qu'un verdict dit."""
    if chemin.startswith(MESURE):
        return True
    if not chemin.startswith("labs/"):
        return False
    return TESTS_DU_LAB in chemin or chemin.endswith(MESURE_PAR_LAB)


def fichiers_indexes() -> list[str]:
    issue = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if issue.returncode != 0:
        print(f"git a repondu {issue.returncode} : {issue.stderr.strip()}", file=sys.stderr)
        # Ne rien pouvoir mesurer n'est pas « tout va bien » : on sort en 2.
        sys.exit(2)
    return [ligne for ligne in issue.stdout.splitlines() if ligne]


def main() -> int:
    indexes = fichiers_indexes()
    if RELEVE not in indexes:
        return 0

    fautifs = [f for f in indexes if mesure_un_verdict(f)]
    if not fautifs:
        return 0

    print(
        f"REFUS : ce commit inscrit « {RELEVE} » ET modifie ce que les verdicts\n"
        "mesurent :\n",
        file=sys.stderr,
    )
    for f in sorted(fautifs):
        print(f"  {f}", file=sys.stderr)
    print(
        "\nUn verdict ecrit dans le meme commit que le code partage qu'il mesure\n"
        "n'est verifiable par personne : le controle de peremption compare les\n"
        "dates de commit, et il n'y a plus rien a comparer. C'est exactement\n"
        "ainsi que vingt et un verdicts sont restes VALIDE le 2026-10-22 alors\n"
        "qu'un defaut du commun les avait tous perimes.\n"
        "\n"
        "Faire deux commits, dans cet ordre :\n"
        "\n"
        "  git reset HEAD validation-labs.json   # sortir le releve de l'index\n"
        "  git commit                            # le correctif, seul\n"
        "  python3 scripts/valider-labs.py       # la campagne, apres lui\n"
        "  git add validation-labs.json && git commit\n",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
