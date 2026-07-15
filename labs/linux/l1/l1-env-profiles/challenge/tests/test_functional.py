"""test_functional.py — l1-env-profiles

Prouve l'ÉTAT de l'environnement obtenu en SOURÇANT env.sh dans un sous-shell :
on lit les variables réellement définies, on vérifie que PATH est bien préfixé,
et qu'un processus enfant hérite des variables (donc qu'elles sont exportées).

Point de départ : répertoire de travail vide. L'apprenant écrit `env.sh`.
On ne touche jamais au vrai profil de l'utilisateur.
"""
from __future__ import annotations

import os
import pathlib
import subprocess

WORK = pathlib.Path(".")
ENV = WORK / "env.sh"
SEP = "\x1f"


def _source_and_read(expr: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", f"source env.sh; {expr}"],
        capture_output=True,
        text=True,
        timeout=15,
    )


def test_env_file_exists() -> None:
    assert ENV.exists(), "env.sh manquant. Crée-le dans challenge/work/."


def test_variables_after_source() -> None:
    """Après source : PROJET=dsoxlab, EDITOR=vim, GREETING réutilise PROJET."""
    res = _source_and_read(
        f'printf "%s{SEP}%s{SEP}%s" "$PROJET" "$EDITOR" "$GREETING"'
    )
    projet, editor, greeting = res.stdout.split(SEP)
    assert projet == "dsoxlab", f"PROJET doit valoir 'dsoxlab', obtenu {projet!r}."
    assert editor == "vim", f"EDITOR doit valoir 'vim', obtenu {editor!r}."
    assert greeting == "Bienvenue sur dsoxlab", (
        "GREETING doit réutiliser $PROJET : GREETING=\"Bienvenue sur $PROJET\". "
        f"Obtenu {greeting!r}."
    )


def test_path_prepended_with_bin() -> None:
    """PATH commence par <workdir>/bin (préfixe, pas suffixe)."""
    res = _source_and_read('printf "%s" "${PATH%%:*}"')
    first = res.stdout
    expected = os.path.join(os.getcwd(), "bin")
    assert first == expected, (
        f"La 1re entrée de PATH doit être {expected!r} (préfixe $PWD/bin), "
        f"obtenu {first!r}. Utilise : export PATH=\"$PWD/bin:$PATH\"."
    )


def test_variables_are_exported() -> None:
    """Un processus enfant hérite de PROJET : la variable est bien exportée."""
    res = _source_and_read('bash -c \'printf "%s" "$PROJET"\'')
    assert res.stdout == "dsoxlab", (
        "PROJET doit être EXPORTé pour qu'un processus enfant le voie "
        "(export PROJET=..., pas seulement PROJET=...). "
        f"L'enfant a vu {res.stdout!r}."
    )
