"""Tests pytest+testinfra — l2-fstab-persist-uuid.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` du formateur sur la VM avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1) pour tester le
travail manuel de l'apprenant.

On prouve l'ÉTAT réel : montage actif, type ext4, et surtout entrée fstab
par UUID (pas par nom de périphérique) dont l'UUID correspond au disque :
c'est ce qui garantit la persistance après reboot.

Le montage actif ne prouve rien à lui seul : il peut venir d'un `mount`
tapé à la main. Et `mount -a` non plus, puisqu'il sort en 0 sur une ligne
fautive déjà montée ou couverte par `nofail`. D'où les deux contrôles
supplémentaires sur la ligne elle-même : son champ type, et le verdict de
`findmnt --verify`, qui relit fstab sans rien monter.
"""
from __future__ import annotations

import re

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"
MOUNT = "/srv/data"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _fstab_line(host) -> str | None:
    """Retourne la ligne fstab non commentée qui monte /srv/data, sinon None."""
    fstab = host.file("/etc/fstab").content_string
    for line in fstab.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2 and fields[1] == MOUNT:
            return stripped
    return None


def test_mounted(host):
    """/srv/data doit être un point de montage actif."""
    assert host.mount_point(MOUNT).exists, message(
        en=f"{MOUNT} is not mounted. After writing the fstab entry: sudo mount -a",
        fr=f"{MOUNT} n'est pas monté. Après avoir écrit l'entrée fstab : sudo mount -a",
    )


def test_filesystem_is_ext4(host):
    """Le filesystem monté sur /srv/data doit être ext4."""
    assert host.mount_point(MOUNT).filesystem == "ext4", message(
        en=f"{MOUNT} must be ext4 (seen: {host.mount_point(MOUNT).filesystem}).",
        fr=f"{MOUNT} doit être un ext4 (vu : {host.mount_point(MOUNT).filesystem}).",
    )


def test_fstab_entry_by_uuid(host):
    """L'entrée fstab de /srv/data doit référencer le disque par UUID, pas /dev/."""
    line = _fstab_line(host)
    assert line is not None, message(
        en=f"No uncommented fstab entry for {MOUNT}. Add: "
        f"UUID=<uuid> {MOUNT} ext4 defaults 0 0",
        fr=f"Aucune entrée fstab non commentée pour {MOUNT}. Ajoutez : "
        f"UUID=<uuid> {MOUNT} ext4 defaults 0 0",
    )
    device = line.split()[0]
    assert device.upper().startswith("UUID="), message(
        en=f"The fstab entry must reference the disk by UUID (the RHCSA trap: a "
        f"/dev/vdX name can change at reboot). Seen: {device!r}. "
        "Get the UUID with blkid.",
        fr=f"L'entrée fstab doit référencer le disque par UUID (piège RHCSA : un "
        f"nom /dev/vdX peut changer au reboot). Vu : {device!r}. "
        "Récupérez l'UUID avec blkid.",
    )


def test_fstab_uuid_matches_device(host):
    """L'UUID écrit dans fstab doit être celui du disque réellement monté."""
    line = _fstab_line(host)
    assert line is not None, message(
        en="fstab entry for /srv/data missing.",
        fr="Entrée fstab pour /srv/data absente.",
    )
    m = re.match(r'UUID=("?)([^"\s]+)\1', line, re.IGNORECASE)
    assert m, message(
        en=f"Unreadable UUID in the fstab entry: {line!r}",
        fr=f"UUID illisible dans l'entrée fstab : {line!r}",
    )
    fstab_uuid = m.group(2)

    source = host.check_output("findmnt -no SOURCE %s", MOUNT)
    real_uuid = host.check_output("blkid -s UUID -o value %s", source)
    assert fstab_uuid == real_uuid, message(
        en=f"The fstab UUID ({fstab_uuid}) does not match the mounted disk "
        f"({real_uuid}). The entry must point at the right filesystem.",
        fr=f"L'UUID de fstab ({fstab_uuid}) ne correspond pas au disque monté "
        f"({real_uuid}). L'entrée doit pointer le bon filesystem.",
    )


def test_fstab_type_matches_filesystem(host):
    """Le 3e champ de l'entrée fstab doit déclarer le bon type.

    Un type erroné passe inaperçu tant que le point de montage est déjà
    actif : `mount -a` ne retouche pas un montage en place et sort en 0.
    Au démarrage, machine froide, le montage échoue.
    """
    line = _fstab_line(host)
    assert line is not None, message(
        en="fstab entry for /srv/data missing.",
        fr="Entrée fstab pour /srv/data absente.",
    )
    fields = line.split()
    assert len(fields) >= 3, message(
        en=f"Incomplete fstab entry: {line!r}. Six fields are expected "
        "(what, where, type, options, dump, pass).",
        fr=f"Entrée fstab incomplète : {line!r}. Six champs sont attendus "
        "(quoi, où, type, options, dump, passe).",
    )
    fstype = fields[2]
    assert fstype in ("ext4", "auto"), message(
        en=f"The type field of the fstab entry is {fstype!r} while the disk "
        "is ext4. A wrong type does not show with mount -a when the "
        "mount point is already active, but it breaks the mount at boot.",
        fr=f"Le champ type de l'entrée fstab vaut {fstype!r} alors que le disque "
        "est en ext4. Un type erroné ne se voit pas avec mount -a quand le "
        "point de montage est déjà actif, mais casse le montage au démarrage.",
    )


@pytest.mark.garde_fou
def test_fstab_verify_reports_no_error(host):
    """`findmnt --verify` ne doit signaler ni parse error ni error.

    C'est le contrôle que `mount -a` ne sait pas faire : il relit
    /etc/fstab sans rien monter et dit ce qui casserait au démarrage.
    Les `warnings` sont tolérés (un autre exercice peut en avoir laissé
    un, par exemple sur un /swapfile) ; les erreurs, non.
    """
    res = host.run("findmnt --verify")
    out = f"{res.stdout}\n{res.stderr}".strip()

    if "Success, no errors or warnings detected" in out:
        return

    m = re.search(r"(\d+)\s+parse errors?,\s*(\d+)\s+errors?", out)
    assert m, message(
        en="Unreadable summary from 'findmnt --verify'. Raw output:\n" + out,
        fr="Résumé de 'findmnt --verify' illisible. Sortie brute :\n" + out,
    )
    parse_errors, errors = int(m.group(1)), int(m.group(2))
    assert parse_errors == 0 and errors == 0, message(
        en="'sudo findmnt --verify' reports errors in /etc/fstab: the "
        "machine will not remount correctly at boot. Fix the "
        f"line, then run 'sudo systemctl daemon-reload'.\n{out}",
        fr="'sudo findmnt --verify' signale des erreurs dans /etc/fstab : la "
        "machine ne remontera pas correctement au démarrage. Corrigez la "
        f"ligne, puis 'sudo systemctl daemon-reload'.\n{out}",
    )
