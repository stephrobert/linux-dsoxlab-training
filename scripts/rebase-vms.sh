#!/usr/bin/env bash
# Fige l'état de base des VM pour l'isolation des labs (scripts/isolation_vm.py).
#
# À LANCER APRÈS TOUT `dsoxlab provision`, sur des VM qui n'ont joué aucun lab :
# ce qui est figé ici est l'état de départ de TOUS les labs VM. Un provision
# recrée les domaines avec un UUID neuf, et libvirt refuse alors de restaurer
# l'ancien état mémoire : sans rebase, valider-labs.py refuse de jouer.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
echo "[rebase] boot complet puis gel mémoire des VM du meta.yml : quelques minutes."
python3 scripts/isolation_vm.py base "$@"
