"""test_functional.py — l1-bash-script

Prouve le COMPORTEMENT du script exécuté, pas son texte : on lance `./rapport.sh`
(ce qui exige un shebang + le bit exécutable), on lit sa sortie et son code de
retour, et on le rejoue sur un cas « tout up » généré à la volée pour prouver que
la condition n'est pas codée en dur.

Point de départ : `serveurs.txt` (up=3, down=2), copié par `dsoxlab run`.
"""
from __future__ import annotations

import pathlib
import re
import stat
import subprocess

from conftest import message

WORK = pathlib.Path(".")
SCRIPT = WORK / "rapport.sh"


def _run(arg: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["./rapport.sh", arg],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def _counts(stdout: str) -> tuple[int, int]:
    up = re.search(r"UP=(\d+)", stdout)
    down = re.search(r"DOWN=(\d+)", stdout)
    assert up and down, message(
        en=f"The output must contain \"UP=<n>\" and \"DOWN=<n>\". Got:\n{stdout}",
        fr=f"La sortie doit contenir « UP=<n> » et « DOWN=<n> ». Obtenu :\n{stdout}",
    )
    return int(up.group(1)), int(down.group(1))


def test_script_exists_shebang_executable() -> None:
    assert SCRIPT.exists(), message(
        en="rapport.sh is missing. Create the script in challenge/work/.",
        fr="rapport.sh manquant. Crée le script dans challenge/work/.",
    )
    first = SCRIPT.read_text(encoding="utf-8").splitlines()[:1]
    assert first and first[0].startswith("#!"), message(
        en="rapport.sh must start with a shebang, e.g. #!/usr/bin/env bash",
        fr="rapport.sh doit commencer par un shebang, ex. #!/usr/bin/env bash",
    )
    assert stat.S_IMODE(SCRIPT.stat().st_mode) & 0o100, message(
        en="rapport.sh must be executable: chmod +x rapport.sh",
        fr="rapport.sh doit être exécutable : chmod +x rapport.sh",
    )


def test_counts_and_exit_on_down() -> None:
    """Sur serveurs.txt : UP=3, DOWN=2, et code de retour non nul (des hôtes down)."""
    res = _run("serveurs.txt")
    up, down = _counts(res.stdout)
    assert (up, down) == (3, 2), message(
        en=f"UP=3 DOWN=2 expected on serveurs.txt, got UP={up} DOWN={down}.",
        fr=f"Attendu UP=3 DOWN=2 sur serveurs.txt, obtenu UP={up} DOWN={down}.",
    )
    assert res.returncode != 0, message(
        en="The script must exit with an error (code != 0) when at least one host is down.",
        fr="Le script doit sortir en erreur (code != 0) quand au moins un hôte est down.",
    )


def test_exit_zero_when_all_up(tmp_path: pathlib.Path) -> None:
    """Sur un fichier tout-up généré : DOWN=0 et code de retour 0 (condition réelle)."""
    f = tmp_path / "tout-up.txt"
    f.write_text("a up\nb up\nc up\n", encoding="utf-8")
    res = _run(str(f))
    up, down = _counts(res.stdout)
    assert (up, down) == (3, 0), message(
        en=f"UP=3 DOWN=0 expected on an all-up file, got UP={up} DOWN={down}.",
        fr=f"Attendu UP=3 DOWN=0 sur un fichier tout-up, obtenu UP={up} DOWN={down}.",
    )
    assert res.returncode == 0, message(
        en="The script must exit with code 0 when no host is down "
        "(the condition must depend on the real number of downs, not be hard-coded).",
        fr="Le script doit sortir avec le code 0 quand aucun hôte n'est down "
        "(la condition doit dépendre du nombre réel de down, pas être codée en dur).",
    )
