"""test_functional.py — l1-permissions-ugo

Prouve l'ÉTAT : les bits de permission réels lus par stat(), pas la commande
tapée. On compare `st_mode & 0o777` à la valeur attendue pour chaque cible.

Point de départ : `secret.txt`, `deploy.sh`, `notes.txt` (copiés par
`dsoxlab run`, en 0644), à ajuster.
"""
from __future__ import annotations

import pathlib
import stat

WORK = pathlib.Path(".")


def _mode(path: pathlib.Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def test_secret_is_private_600() -> None:
    """secret.txt = 0600 : lisible/écrivable par le seul propriétaire."""
    f = WORK / "secret.txt"
    assert f.exists(), "secret.txt introuvable — lance : dsoxlab run l1-permissions-ugo"
    assert _mode(f) == 0o600, (
        f"secret.txt doit être en 0600 (rw-------), trouvé {oct(_mode(f))}. "
        "Utilise : chmod 600 secret.txt"
    )


def test_script_is_executable_750() -> None:
    """deploy.sh = 0750 : exécutable par le propriétaire et le groupe, rien pour les autres."""
    f = WORK / "deploy.sh"
    assert f.exists(), "deploy.sh introuvable — lance : dsoxlab run l1-permissions-ugo"
    assert _mode(f) == 0o750, (
        f"deploy.sh doit être en 0750 (rwxr-x---), trouvé {oct(_mode(f))}. "
        "Utilise : chmod 750 deploy.sh"
    )


def test_notes_group_readable_640() -> None:
    """notes.txt = 0640 : le groupe lit, les autres non."""
    f = WORK / "notes.txt"
    assert f.exists(), "notes.txt introuvable — lance : dsoxlab run l1-permissions-ugo"
    assert _mode(f) == 0o640, (
        f"notes.txt doit être en 0640 (rw-r-----), trouvé {oct(_mode(f))}. "
        "Utilise : chmod 640 notes.txt"
    )


def test_private_dir_700() -> None:
    """prive/ = répertoire en 0700 : traversable et listable par le seul propriétaire."""
    d = WORK / "prive"
    assert d.exists() and d.is_dir(), (
        "Le répertoire prive/ manque. Crée-le : mkdir prive"
    )
    assert _mode(d) == 0o700, (
        f"prive/ doit être en 0700 (rwx------), trouvé {oct(_mode(d))}. "
        "Utilise : chmod 700 prive"
    )
