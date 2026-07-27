#!/usr/bin/env python3
"""Rejoue les solutions de référence et prouve qu'elles marchent encore.

Raison d'être : une montée de version (noyau, systemd, distribution, provider)
peut casser une solution sans que personne ne s'en aperçoive, parce que les
tests d'un lab ne tournent que si quelqu'un le joue. Ce script les joue tous et
enregistre le verdict dans ``solution/verified-with.json``.

Le rejeu lui-même n'est pas réimplémenté ici : il vit déjà dans la fixture
autouse ``_apply_lab_state`` du ``conftest.py`` racine, qui déchiffre la
solution (``.vault-pass``) et l'applique avant les tests. Ce script se contente
de lancer pytest **sans** ``LAB_NO_REPLAY``, lab par lab.

    python3 scripts/verify-solutions.py                # tout ce qui est jouable
    python3 scripts/verify-solutions.py --lab l1-first-terminal
    python3 scripts/verify-solutions.py --runtime shell
    python3 scripts/verify-solutions.py --check        # sort en 1 si une solution casse
    python3 scripts/verify-solutions.py --negative     # + contrôle négatif

Le contrôle négatif (``--negative``) rejoue les mêmes tests avec
``LAB_NO_REPLAY=1``, sans appliquer la solution : ils doivent alors **échouer**.
Un test qui passe dans les deux sens ne prouve rien, c'est le défaut que ce
mode attrape.

Les labs ``vm`` exigent une infrastructure provisionnée (``dsoxlab provision``).
Sans elle, ils sont comptés **ignorés**, jamais en échec : un harnais absent
n'est pas une régression de contenu.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LABS = REPO / "labs"
SOLUTIONS = REPO / "solution"
RECORD = SOLUTIONS / "verified-with.json"
VAULT_PASS = REPO / ".vault-pass"

VM_RUNTIMES = {"vm", "kvm", "incus"}


# ── découverte ────────────────────────────────────────────────────────────────

def _charger_yaml(chemin: Path) -> dict:
    import yaml  # dépendance déjà présente via dsoxlab / ansible

    with chemin.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class Lab:
    """Un lab et sa solution de référence, tels qu'ils sont sur le disque."""

    def __init__(self, lab_yaml: Path) -> None:
        data = _charger_yaml(lab_yaml)
        self.chemin = lab_yaml.parent
        self.relatif = self.chemin.relative_to(LABS)
        self.id = str(data.get("id") or self.chemin.name)
        runtime = data.get("runtime") or {}
        self.runtime = str(runtime.get("type", "shell"))
        self.tests = self.chemin / "challenge" / "tests"

    @property
    def est_vm(self) -> bool:
        return self.runtime in VM_RUNTIMES

    @property
    def solution(self) -> Path | None:
        """`solution.yaml` pour un lab vm, `solution.sh` pour un lab shell."""
        base = SOLUTIONS / self.relatif
        candidat = base / ("solution.yaml" if self.est_vm else "solution.sh")
        return candidat if candidat.is_file() else None


def decouvrir(
    filtre_id: str | None, filtre_runtime: str, filtre_section: str | None = None
) -> list[Lab]:
    labs = [Lab(y) for y in sorted(LABS.rglob("lab.yaml"))]
    if filtre_id:
        labs = [lab for lab in labs if lab.id == filtre_id]
        if not labs:
            sys.exit(f"Lab inconnu : {filtre_id}")
    if filtre_section:
        # `labs/linux/l2/l2-swap-management` → section « l2 ».
        labs = [lab for lab in labs
                if len(lab.relatif.parts) > 1 and lab.relatif.parts[1] == filtre_section]
        if not labs:
            sys.exit(f"Section sans lab : {filtre_section}")
    if filtre_runtime == "shell":
        labs = [lab for lab in labs if not lab.est_vm]
    elif filtre_runtime == "vm":
        labs = [lab for lab in labs if lab.est_vm]
    return labs


# ── pré-conditions ────────────────────────────────────────────────────────────

def _interpreteur_ok() -> bool:
    """pytest est-il importable par l'interpréteur courant ?

    Le piège classique : lancé par `/usr/bin/python3`, ce script verrait
    **toutes** les solutions échouer d'un coup, ce qui ressemble à une
    régression massive alors que c'est le harnais qui manque.
    """
    try:
        import pytest  # noqa: F401
        return True
    except ImportError:
        return False


def _infra_disponible() -> bool:
    """Les VM du meta.yml sont-elles provisionnées et joignables ?"""
    try:
        from dsoxlab.discovery.repo import read_repo_metadata
        from dsoxlab.infra.inventory import read_terraform_outputs
    except ImportError:
        return False
    try:
        meta = read_repo_metadata(REPO)
        if meta is None:
            return False
        sorties = read_terraform_outputs(meta)
        return bool(sorties)
    except Exception:  # noqa: BLE001 — sonde best-effort : tout echec = pas d infra
        return False


# ── exécution ─────────────────────────────────────────────────────────────────

def reinitialiser(lab: Lab) -> tuple[bool, str]:
    """Remet le lab dans son état de départ, via `dsoxlab reset`.

    Indispensable avant un contrôle négatif : sans elle, la passe précédente
    a laissé le travail fait (le workdir d'un lab shell est gitignoré, donc
    rien ne le remet en place tout seul), et les tests passent « sans la
    solution » pour une raison qui n'a rien à voir avec leur qualité. C'est
    le faux rouge que ce script produisait avant cette étape.
    """
    proc = subprocess.run(
        ["dsoxlab", "reset", lab.id],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    if proc.returncode == 0:
        return True, ""
    # La cause vit dans la sortie de dsoxlab : sans elle, un « reset
    # impossible » ne dit pas si le playbook est cassé, si l'hôte est
    # injoignable, ou si le lab précédent a laissé le disque occupé.
    lignes = [ligne.strip() for ligne in (proc.stdout + proc.stderr).splitlines()
              if ligne.strip()]
    interessantes = [ligne for ligne in lignes
                     if "✘" in ligne or "failed" in ligne.lower()]
    return False, (interessantes[-1] if interessantes else (lignes[-1] if lignes else "cause inconnue"))


def _hotes_avec_disque_additionnel() -> list[str]:
    """Les hôtes du meta.yml qui portent un second disque."""
    meta = _charger_yaml(REPO / "meta.yml")
    hosts = ((meta.get("infra") or {}).get("hosts") or [])
    return [h["name"] for h in hosts if h.get("extra_disk_gb")]


def etat_disque_additionnel() -> str:
    """Le disque additionnel est-il rendu vierge après le lab ?

    Les labs partagent les mêmes VM, donc le même second disque. Un lab qui
    laisse une partition derrière lui ne casse pas ses propres tests : il
    casse le **suivant**, avec un « reset impossible » qui accuse un innocent.
    Ce contrôle nomme le vrai coupable au moment où il salit.

    Rend une description de ce qui occupe le disque, ou une chaîne vide.
    """
    ssh_config = Path.home() / ".cache" / "dsoxlab" / REPO.name / "ssh_config"
    if not ssh_config.is_file():
        return ""  # pas d'inventaire généré : rien à contrôler
    for hote in _hotes_avec_disque_additionnel():
        proc = subprocess.run(
            ["ssh", "-F", str(ssh_config), "-o", "LogLevel=ERROR", hote,
             "sudo lsblk -no NAME /dev/vdb 2>/dev/null | tail -n +2"],
            capture_output=True, text=True, timeout=60, check=False,
        )
        restes = " ".join(proc.stdout.split())
        if restes:
            return f"{hote} : {restes}"
    return ""


def jouer(lab: Lab, *, rejeu: bool) -> tuple[bool, str]:
    """Lance les tests du lab. `rejeu=False` pose LAB_NO_REPLAY=1."""
    env = dict(os.environ)
    if rejeu:
        env.pop("LAB_NO_REPLAY", None)
    else:
        env["LAB_NO_REPLAY"] = "1"

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(lab.tests), "-q", "--no-header"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    lignes = [ligne for ligne in proc.stdout.strip().splitlines() if ligne.strip()]
    resume = lignes[-1] if lignes else "aucune sortie"
    return proc.returncode == 0, resume


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--lab", help="ne traiter que ce lab (son id)")
    parseur.add_argument("--section", help="ne traiter que cette section (l1, l2, lfcs…)")
    parseur.add_argument("--runtime", choices=("all", "shell", "vm"), default="all")
    parseur.add_argument("--check", action="store_true",
                         help="sortir en 1 si une solution casse")
    parseur.add_argument("--negative", action="store_true",
                         help="vérifier aussi que les tests échouent sans la solution")
    args = parseur.parse_args()

    if not _interpreteur_ok():
        print(
            "pytest n'est pas importable par cet interpréteur "
            f"({sys.executable}).\n"
            "Relance avec le python qui porte pytest, par exemple :\n"
            "    ~/Projets/dsoxlab/.venv/bin/python scripts/verify-solutions.py",
            file=sys.stderr,
        )
        return 2

    labs = decouvrir(args.lab, args.runtime, args.section)
    infra = _infra_disponible()
    if not infra and any(lab.est_vm for lab in labs):
        print("Infra non provisionnée : les labs vm seront ignorés "
              "(dsoxlab provision pour les jouer).\n")

    verdicts: dict[str, dict] = {}
    verts = rouges = ignores = 0

    for lab in labs:
        if not lab.tests.is_dir():
            verdicts[lab.id] = {"etat": "ignoré", "motif": "aucun test"}
            ignores += 1
            continue
        if lab.solution is None:
            verdicts[lab.id] = {"etat": "ignoré", "motif": "aucune solution"}
            ignores += 1
            print(f"  ⊘ {lab.id:<34} aucune solution de référence")
            continue
        if lab.est_vm and not infra:
            verdicts[lab.id] = {"etat": "ignoré", "motif": "infra absente"}
            ignores += 1
            continue
        if not VAULT_PASS.is_file():
            verdicts[lab.id] = {"etat": "ignoré", "motif": ".vault-pass absent"}
            ignores += 1
            continue

        # Réinitialisation systématique, pas seulement pour le contrôle négatif.
        # Rejouer une solution, c'est la rejouer depuis l'état de départ du lab :
        # sur un état déjà résolu, une solution non idempotente échoue pour une
        # raison qui ne dit rien de sa validité. Cas vécu : `l1-git-basics` sort
        # en rc=1 sur « nothing to commit, working tree clean », et `l1-links-
        # hard-sym` de même, alors que les deux sont sains après un reset.
        reset_ok, cause = reinitialiser(lab)
        if not reset_ok:
            verdicts[lab.id] = {"etat": "ignoré", "motif": f"reset impossible : {cause}"}
            ignores += 1
            print(f"  ⊘ {lab.id:<34} reset impossible : {cause[:70]}")
            continue

        # Etat du disque partage AVANT que le lab travaille : ce qui est deja
        # la vient du lab precedent, pas de celui-ci.
        avant = etat_disque_additionnel() if lab.est_vm else ""

        # Contrôle négatif avant le rejeu : l'inverse mesurerait ce que le
        # rejeu vient de poser.
        faux_positif = False
        if args.negative:
            passe_sans_solution, _ = jouer(lab, rejeu=False)
            faux_positif = passe_sans_solution

        ok, resume = jouer(lab, rejeu=True)
        entree = {"etat": "vert" if ok else "ROUGE", "runtime": lab.runtime,
                  "resume": resume}

        if faux_positif:
            entree["etat"] = "ROUGE"
            entree["motif"] = ("les tests passent SANS la solution : "
                               "ils ne prouvent rien")
            ok = False

        # Le lab a fini : on joue son cleanup, puis on verifie qu'il rend bien
        # le disque partage. Nettoyer ici sert deux fois : ca prouve que le
        # cleanup fait son travail, et ca laisse la VM propre pour le lab
        # suivant, au lieu de lui faire porter le chapeau.
        # Nettoyer MEME quand les tests echouent : un lab en echec qu'on laisse
        # en place pollue tous les suivants (haproxy garde le port 80, un VG
        # garde le disque…) et transforme un rouge isole en cascade de rouges
        # qui accusent des innocents.
        if lab.est_vm:
            subprocess.run(
                ["dsoxlab", "clean", lab.id, "--yes"],
                cwd=REPO, capture_output=True, text=True, check=False,
            )
            apres = etat_disque_additionnel()
            if ok and apres and apres != avant:
                entree["etat"] = "ROUGE"
                entree["motif"] = (
                    f"cleanup incomplet : le disque etait « {avant or 'vierge'} » "
                    f"avant le lab et « {apres} » apres. Le lab suivant heritera "
                    "de cet etat et echouera a sa place."
                )
                ok = False

        verdicts[lab.id] = entree
        if ok:
            verts += 1
            print(f"  ✔ {lab.id:<34} {resume}")
        else:
            rouges += 1
            print(f"  ✘ {lab.id:<34} {entree.get('motif', resume)}")

    print(f"\n{verts} vert(s), {rouges} rouge(s), {ignores} ignoré(s) "
          f"sur {len(labs)} lab(s).")

    if args.lab is None and args.section is None and args.runtime == "all":
        SOLUTIONS.mkdir(exist_ok=True)
        RECORD.write_text(
            json.dumps(
                {
                    "verifie_le": datetime.now(UTC).isoformat(timespec="seconds"),
                    "python": sys.version.split()[0],
                    "labs": verdicts,
                },
                indent=2,
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"Verdict enregistré dans {RECORD.relative_to(REPO)}")

    return 1 if (args.check and rouges) else 0


if __name__ == "__main__":
    sys.exit(main())
