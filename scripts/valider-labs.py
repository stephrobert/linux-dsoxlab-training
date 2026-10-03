#!/usr/bin/env python3
"""Éprouve chaque lab dans les DEUX sens, par dsoxlab, et écrit son verdict.

Pourquoi ce script existe
-------------------------
`scripts/test-all.sh` rejoue la solution de référence contre les tests du lab,
par la fixture `_apply_lab_state` du `conftest.py`. C'est utile, et cela prouve
exactement une chose : **la solution passe les tests**.

Cela ne prouve pas l'autre moitié, **les tests échouent avant le travail**. Un
lab dont les tests sont verts sur l'état de départ ne mesure rien, et rien dans
le fichier ne le laisse deviner. Le catalogue Kubernetes a trouvé ainsi cinq
labs en un jour, et six ont été trouvés ici (issue #17), dont un qui rendait
50/100 sans qu'on ait touché à quoi que ce soit.

Ce que le script fait, et rien de plus
--------------------------------------
Il **enchaîne les commandes dsoxlab**, il ne les réimplémente pas. Pour chaque
lab :

    dsoxlab clean <id>     on part d'un état connu
    (ses VM reviennent à leur base figée : scripts/isolation_vm.py)
    dsoxlab run   <id>     l'état de départ est posé
    dsoxlab check <id>     DOIT rendre 0 : le travail n'est pas fait
    (la solution de référence est déchiffrée dans le workdir et jouée)
    dsoxlab check <id>     DOIT rendre 100
    dsoxlab clean <id>     et il ne doit rien rester

Le verdict va dans `validation-labs.json`, versionné : c'est la trace qui
manquait, et elle distingue « livrable » de « validé ».

Ce que le script surveille en plus
----------------------------------
**Les traces.** Un lab qui laisse un conteneur Docker derrière lui fait tomber
le suivant, et le message ne parle alors ni du lab ni du conteneur. Mesuré le
2026-09-24 sur ce dépôt : un conteneur `floci-ec2-*` orphelin retenait le port
2201, et la création d'instance suivante échouait sur « Bind for 0.0.0.0:2201
failed », sans un mot sur la cause. Le script photographie donc les conteneurs
avant et après, et nomme ce qui a été laissé.

Ce qu'il ne peut pas faire
--------------------------
Il ne juge pas la JUSTESSE d'un lab. Un lab peut rendre 0 puis 100 en ne
mesurant rien d'intéressant. Le cycle prouve que les tests discriminent l'état
de départ de l'état d'arrivée, pas que la question posée vaut la peine.

Usage :
    python3 scripts/valider-labs.py                    # tout le catalogue
    python3 scripts/valider-labs.py --lab <id>          # un seul lab
    python3 scripts/valider-labs.py --section capstone
    python3 scripts/valider-labs.py --check             # échoue si un lab est ROUGE
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from isolation_vm import IsolationEteinte, hotes_du_lab, snapshot_reset
from lecture_yaml import YamlIllisible, lire_yaml

RACINE = Path(__file__).resolve().parent.parent
LABS = RACINE / "labs"
SOLUTIONS = RACINE / "solution"
VERDICTS = RACINE / "validation-labs.json"
VAULT = RACINE / ".vault-pass"

# `dsoxlab check` affiche « Score : 87 / 100 pts » ; on lit le premier nombre.
SCORE = re.compile(r"Score\s*:\s*(\d+)\s*/\s*100")
TESTS = re.compile(r"Tests\s*:\s*[^\d]*(\d+)/(\d+)")

# Un lab qui skippe n'est ni validé ni rouge : il n'a pas pu être joué.
MARQUES_DE_SKIP = ("skipped", "SKIPPED", "Lab non joué")


@dataclass
class Verdict:
    """Ce qu'on a mesuré d'un lab, et ce qui permet d'en juger."""

    id: str
    chemin: str
    verdict: str = "INCONNU"
    score_avant: int | None = None
    score_apres: int | None = None
    tests: str | None = None
    duree_s: float = 0.0
    traces: list[str] = field(default_factory=list)
    pourquoi: str = ""


def _dsoxlab(*args: str, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, LAB_HOME=str(RACINE))
    return subprocess.run(
        ["dsoxlab", *args],
        cwd=RACINE,
        env=env,
        input="y\n",
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _score(sortie: str) -> int | None:
    trouve = SCORE.search(sortie)
    return int(trouve.group(1)) if trouve else None


def _tests(sortie: str) -> str | None:
    trouve = TESTS.search(sortie)
    return f"{trouve.group(1)}/{trouve.group(2)}" if trouve else None


def _conteneurs() -> set[str]:
    """Les conteneurs Docker présents, pour comparer avant et après."""
    if not shutil.which("docker"):
        return set()
    proc = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {ligne.strip() for ligne in proc.stdout.splitlines() if ligne.strip()}


def labs_du_catalogue() -> list[tuple[str, Path]]:
    """[(id, répertoire), ...] pour tout lab porteur d'un lab.yaml."""
    trouves = []
    for contrat in sorted(LABS.rglob("lab.yaml")):
        try:
            donnees = lire_yaml(contrat)
        except YamlIllisible as erreur:
            print(f"  lab illisible, écarté : {erreur}", file=sys.stderr)
            continue
        identifiant = donnees.get("id")
        if identifiant:
            trouves.append((identifiant, contrat.parent))
    return trouves


def _python_dsoxlab() -> str:
    """Le Python de l'outil dsoxlab : celui qui porte pytest, testinfra et dsoxlab."""
    binaire = shutil.which("dsoxlab")
    if binaire:
        candidat = Path(binaire).resolve().parent / "python"
        if candidat.is_file():
            return str(candidat)
    return sys.executable


def _poser_la_solution(lab: Path) -> str | None:
    """Pose la solution de référence par le conftest du catalogue.

    Ce catalogue sait déjà rejouer une solution : la fixture `_apply_lab_state`
    joue `solution.sh` dans le workdir d'un lab shell, et `solution.yaml` par
    ansible-runner sur la cible d'un lab vm, avec l'inventaire de dsoxlab. On
    lance donc la suite du lab SANS `LAB_NO_REPLAY` : la solution est posée,
    puis jugée ; c'est le `dsoxlab check` qui suit qui fait foi.

    Rend un message d'erreur, ou None si la solution a pu être posée.
    """
    rel = lab.relative_to(LABS)
    source = SOLUTIONS / rel
    if not source.is_dir() or not any(source.rglob("*")):
        return f"aucune solution de référence sous solution/{rel}"
    tests = lab / "challenge" / "tests"
    if not tests.is_dir():
        return "aucune suite de tests sous challenge/tests"
    env = {k: v for k, v in os.environ.items() if k not in ("LAB_NO_REPLAY", "VIRTUAL_ENV")}
    proc = subprocess.run(
        [_python_dsoxlab(), "-m", "pytest", str(tests), "-q", "-p", "no:cacheprovider", "--no-header"],
        cwd=RACINE,
        env=env,
        capture_output=True,
        text=True,
        timeout=1800,
        check=False,
    )
    sortie = proc.stdout + proc.stderr
    # Messages d'échec du rejeu, tels que le conftest de ce catalogue les écrit.
    if "solution.yaml a échoué" in sortie or "solution.sh a échoué" in sortie:
        return f"la solution n'a pas pu être posée : {sortie[-400:]}"
    return None


def valider(identifiant: str, lab: Path) -> Verdict:
    """Le cycle complet sur un lab."""
    v = Verdict(id=identifiant, chemin=str(lab.relative_to(LABS)))
    debut = time.monotonic()
    avant = _conteneurs()

    try:
        _dsoxlab("clean", identifiant, timeout=300)

        # Les VM du lab reviennent à leur base figée AVANT le run : sans cela,
        # le premier check note aussi ce qu'ont laissé les labs précédents.
        # Mesuré le 2026-10-03 : 23 labs sur 86 rendaient des points avant
        # tout travail, et le résidu ne se distinguait pas d'un test mal conçu.
        try:
            snapshot_reset(hotes_du_lab(lab))
        except IsolationEteinte as erreur:
            v.verdict = "ROUGE"
            v.pourquoi = f"isolation impossible : {erreur}"
            return v

        pose = _dsoxlab("run", identifiant)
        if pose.returncode != 0:
            v.verdict = "ROUGE"
            v.pourquoi = f"`run` a échoué : {(pose.stderr or pose.stdout)[-300:]}"
            return v

        # Sens « 0 » : les tests doivent échouer sur l'état de départ.
        premier = _dsoxlab("check", identifiant)
        sortie = premier.stdout + premier.stderr
        if any(m in sortie for m in MARQUES_DE_SKIP) and _score(sortie) is None:
            v.verdict = "SKIP"
            v.pourquoi = "le lab se skippe : prérequis absent (service ou compte)"
            return v

        v.score_avant = _score(sortie)
        if v.score_avant is None:
            v.verdict = "ROUGE"
            v.pourquoi = f"aucun score lisible au premier check : {sortie[-300:]}"
            return v
        if v.score_avant != 0:
            v.verdict = "ROUGE"
            v.pourquoi = (
                f"le lab rend {v.score_avant}/100 AVANT tout travail. Un test vert "
                "sur l'état de départ n'est pas un test, c'est une hypothèse du "
                "setup."
            )
            return v

        # Sens « 100 » : la solution de référence doit tout passer.
        souci = _poser_la_solution(lab)
        if souci:
            v.verdict = "ROUGE"
            v.pourquoi = souci
            return v

        second = _dsoxlab("check", identifiant)
        sortie = second.stdout + second.stderr
        v.score_apres = _score(sortie)
        v.tests = _tests(sortie)

        # On juge sur les TESTS, pas sur le score. Mesuré le 2026-09-25 :
        # `essential-commands` rendait 8/8 tests et 90/100, parce qu'un indice
        # de coût 10 avait été révélé sur ce poste le 24. Le score porte
        # l'historique local de l'apprenant, le lab n'y est pour rien, et un
        # validateur qui le lit accuse un lab juste.
        reussis, total = (v.tests or "0/0").split("/")
        if not total or total == "0":
            v.verdict = "ROUGE"
            v.pourquoi = f"aucun test lisible après la solution : {sortie[-300:]}"
            return v
        if reussis != total:
            v.verdict = "ROUGE"
            v.pourquoi = (
                f"la solution de référence ne passe que {v.tests} tests. Soit "
                "elle est fausse, soit un test exige l'impossible."
            )
            return v

        v.verdict = "VALIDE"

    except subprocess.TimeoutExpired as erreur:
        v.verdict = "ROUGE"
        v.pourquoi = f"délai dépassé : {erreur}"
    finally:
        _dsoxlab("clean", identifiant, timeout=300)
        v.duree_s = round(time.monotonic() - debut, 1)

        # Les traces : ce que le lab a laissé derrière lui.
        #
        # Les conteneurs préfixés `dsoxlab-` sont ceux que l'outil gère, y
        # compris les services qu'un lab déclare : il les arrête avec la
        # session, et les compter ici accuse le lab pour le travail de l'outil.
        # Mesuré le 2026-09-25 : `write-code-tfvars-files`, qui ne déclare
        # AUCUN service, s'est vu attribuer un `dsoxlab-dsoxlab-test-net-pytest-db`
        # apparu pendant sa fenêtre et créé par tout autre chose.
        #
        # Ce qu'on surveille vraiment, ce sont les conteneurs qu'un service
        # ENGENDRE, comme les `floci-ec2-*` qui retiennent un port SSH et font
        # tomber le lab suivant.
        laisses = {
            c for c in _conteneurs() - avant if not c.startswith("dsoxlab-")
        }
        if laisses:
            v.traces = sorted(laisses)
            if v.verdict == "VALIDE":
                v.verdict = "ROUGE"
                v.pourquoi = (
                    f"le lab laisse {len(laisses)} conteneur(s) derrière lui : "
                    f"{v.traces}. C'est le lab suivant qui en paiera le prix."
                )

    return v


def charger_verdicts() -> dict:
    if not VERDICTS.is_file():
        return {}
    try:
        return json.loads(VERDICTS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def version(*commande: str) -> str:
    try:
        proc = subprocess.run(commande, capture_output=True, text=True, check=False)
        return proc.stdout.splitlines()[0].strip() if proc.stdout else "inconnue"
    except (OSError, IndexError):
        return "inconnue"


def main() -> int:
    analyseur = argparse.ArgumentParser(
        description="Éprouve chaque lab dans les deux sens et écrit son verdict.",
    )
    analyseur.add_argument("--lab", help="un seul lab, par son id")
    analyseur.add_argument("--section", help="une section, par son répertoire")
    analyseur.add_argument(
        "--check",
        action="store_true",
        help="ne rejoue rien ; échoue si un verdict enregistré est ROUGE",
    )
    arguments = analyseur.parse_args()

    if arguments.check:
        enregistres = charger_verdicts().get("labs", {})
        if not enregistres:
            print("aucun verdict enregistré : lancez le script sans --check", file=sys.stderr)
            return 1
        rouges = [i for i, v in enregistres.items() if v.get("verdict") == "ROUGE"]
        if rouges:
            print(f"{len(rouges)} lab(s) ROUGE : {rouges}", file=sys.stderr)
            return 1
        print(f"{len(enregistres)} labs, aucun ROUGE")
        return 0

    if not VAULT.is_file():
        print(".vault-pass absent : les solutions ne peuvent pas être déchiffrées.", file=sys.stderr)
        return 1

    a_jouer = labs_du_catalogue()
    if arguments.lab:
        a_jouer = [(i, p) for i, p in a_jouer if i == arguments.lab]
    if arguments.section:
        a_jouer = [
            (i, p) for i, p in a_jouer if str(p.relative_to(LABS)).startswith(arguments.section)
        ]
    if not a_jouer:
        print("aucun lab à jouer avec ces critères", file=sys.stderr)
        return 1

    print(f"{len(a_jouer)} lab(s) à éprouver dans les deux sens\n")

    resultats = charger_verdicts().get("labs", {})
    for rang, (identifiant, lab) in enumerate(a_jouer, start=1):
        print(f"[{rang}/{len(a_jouer)}] {identifiant} ... ", end="", flush=True)
        v = valider(identifiant, lab)
        resultats[identifiant] = asdict(v)
        detail = f"{v.score_avant} -> {v.score_apres}" if v.score_avant is not None else ""
        print(f"{v.verdict} {detail} ({v.duree_s}s)")
        if v.pourquoi:
            print(f"      {v.pourquoi}")

        # On écrit au fil de l'eau : une campagne interrompue garde ce qu'elle
        # a mesuré.
        VERDICTS.write_text(
            json.dumps(
                {
                    "genere_le": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "act": version("act", "--version"),
                    "dsoxlab": version("dsoxlab", "--version"),
                    "labs": dict(sorted(resultats.items())),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    comptes: dict[str, int] = {}
    for v in resultats.values():
        comptes[v["verdict"]] = comptes.get(v["verdict"], 0) + 1
    print("\n" + ", ".join(f"{n} {etat}" for etat, n in sorted(comptes.items())))
    print(f"verdicts écrits dans {VERDICTS.relative_to(RACINE)}")

    return 1 if comptes.get("ROUGE") else 0


if __name__ == "__main__":
    raise SystemExit(main())
