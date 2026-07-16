"""Tests pytest+testinfra — lfcs-mount-cifs (lab multi-hôte).

Les tests tournent côté CLIENT (ubuntu-lfcs-1). La fixture autouse
`_apply_lab_state` (conftest.py racine) joue le `solution.yaml` chiffré du
formateur avant les tests (mode CI). En `dsoxlab check`, elle est désactivée
(LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le partage du serveur est monté en CIFS, le fichier servi est
lisible (donc le montage s'authentifie vraiment), l'entrée fstab est persistante
avec _netdev, et le mot de passe n'est PAS dans /etc/fstab (lisible par tous)
mais dans un fichier credentials en 0600.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

CLIENT_HOST = "ubuntu-lfcs-1.lab"
MOUNT = "/mnt/labshare"
PASSWORD = "labpass123"


@pytest.fixture(scope="module")
def host():
    return lab_host(CLIENT_HOST)


def _fstab_line(host) -> str | None:
    """Retourne la ligne fstab qui monte MOUNT, sinon None."""
    fstab = host.file("/etc/fstab").content_string
    for line in fstab.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2 and fields[1] == MOUNT:
            return stripped
    return None


def _credentials_path(host) -> str | None:
    """Extrait le chemin du fichier credentials= de la ligne fstab."""
    line = _fstab_line(host)
    if line is None:
        return None
    fields = line.split()
    if len(fields) < 4:
        return None
    for opt in fields[3].split(","):
        if opt.startswith("credentials="):
            return opt.split("=", 1)[1]
    return None


def test_mounted(host):
    """/mnt/labshare doit être monté (le partage SMB du serveur)."""
    assert host.mount_point(MOUNT).exists, (
        f"{MOUNT} n'est pas monté. Après l'entrée fstab : sudo mount -a"
    )


def test_type_is_cifs(host):
    """Le montage doit être de type CIFS."""
    fstype = host.check_output("findmnt -no FSTYPE %s", MOUNT)
    assert fstype == "cifs", (
        f"{MOUNT} doit être un montage CIFS (vu : {fstype!r})."
    )


def test_served_file_readable(host):
    """Le fichier servi par le serveur doit être lisible via le montage."""
    f = host.file(f"{MOUNT}/README.txt")
    assert f.exists, (
        f"{MOUNT}/README.txt introuvable : le montage CIFS ne sert pas le "
        "contenu du serveur (mauvais partage, ou authentification échouée)."
    )


def test_fstab_persistent_netdev(host):
    """L'entrée fstab doit être persistante avec _netdev (montage réseau)."""
    line = _fstab_line(host)
    assert line is not None, (
        f"Aucune entrée fstab pour {MOUNT} : le montage disparaîtrait au "
        "reboot. Ajoute : //<serveur>/labshare /mnt/labshare cifs "
        "_netdev,credentials=<fichier> 0 0"
    )
    fields = line.split()
    assert len(fields) >= 4 and fields[2] == "cifs", (
        f"L'entrée fstab de {MOUNT} doit être de type cifs (vu : {line!r})."
    )
    assert "_netdev" in fields[3].split(","), (
        "L'option _netdev est requise pour un montage réseau (attend le réseau "
        f"au boot). Vu : {fields[3]!r}."
    )


def test_password_not_in_fstab(host):
    """/etc/fstab est lisible par tous : le mot de passe ne doit pas y être."""
    # On exige d'abord l'entrée : sinon « pas de mot de passe » serait vrai
    # trivialement sur un fstab vierge, et le test ne prouverait rien.
    assert _fstab_line(host) is not None, (
        f"Aucune entrée fstab pour {MOUNT} : rien à vérifier tant que le "
        "montage n'est pas déclaré."
    )
    fstab = host.file("/etc/fstab").content_string
    assert PASSWORD not in fstab, (
        "Le mot de passe SMB est écrit en clair dans /etc/fstab, qui est "
        "lisible par tous les utilisateurs. Utilise l'option "
        "credentials=<fichier> et mets le mot de passe dans ce fichier."
    )


def test_credentials_file_is_protected(host):
    """Le fichier credentials doit exister et n'être lisible que par root."""
    path = _credentials_path(host)
    assert path is not None, (
        "L'entrée fstab doit utiliser l'option credentials=<fichier> pour "
        "garder le mot de passe hors de /etc/fstab."
    )
    creds = host.file(path)
    assert creds.exists, (
        f"Le fichier credentials {path} référencé dans /etc/fstab n'existe pas."
    )
    assert creds.mode == 0o600, (
        f"Le fichier credentials {path} contient un mot de passe : il doit être "
        f"en 0600 (vu : {oct(creds.mode)})."
    )
