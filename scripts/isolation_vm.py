"""Isolation des labs VM par overlay qcow2 : chaque lab repart d'une VM neuve.

Pourquoi
--------
Les labs de ce catalogue partagent trois VM. Sans isolation, chaque lab note
l'état laissé par ses prédécesseurs : un service démarré, une ligne de fstab,
un `minlen` de pwquality. Mesuré le 2026-10-03 : 23 labs sur 86 rendaient des
points AVANT tout travail, et rien ne permettait de distinguer un test mal
conçu d'un résidu du lab joué juste avant.

Comment
-------
Repris du catalogue Ansible, qui l'a éprouvé sur 113 labs. Les VM tournent en
UEFI (pflash) : `virsh snapshot-revert` y est refusé. On obtient le même effet
avec un overlay qcow2 jetable :

- `snapshot_base()` fait du disque frais une base IMMUABLE (`<vol>.base.qcow2`)
  et pose un overlay vide sous le nom que le domaine référence déjà ; puis,
  après un boot complet, il FIGE l'état mémoire (`managedsave`) et le disque
  post-boot (`<vol>.qcow2.postboot`).
- `snapshot_reset()` recopie le disque post-boot et l'état mémoire figé : la
  VM revient bootée, services prêts, en quelques secondes et sans reboot.

`snapshot_base()` se lance sur des VM FRAÎCHES, juste après `dsoxlab provision`
(`scripts/rebase-vms.sh`). Tout `provision` recrée les domaines avec un UUID
neuf, et libvirt refuse de restaurer un état mémoire vers un autre UUID : il
faut alors rebaser.

Ce module n'importe que la bibliothèque standard et `yaml` : `valider-labs.py`
tourne avec le Python du système, sans pytest ni dsoxlab.
"""

from __future__ import annotations

import ipaddress
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
META = RACINE / "meta.yml"
CLE_SSH = RACINE / "ssh" / "id_ed25519"
POOL = Path("/var/lib/libvirt/images")


class IsolationEteinte(RuntimeError):
    """L'isolation n'a pas pu s'appliquer : le verdict du lab ne vaudrait rien."""


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(
            f"Commande échouée (exit {res.returncode}) : {' '.join(cmd)}\n"
            f"{res.stdout}\n{res.stderr}"
        )
    return res


def _infra() -> dict:
    meta = yaml.safe_load(META.read_text(encoding="utf-8")) or {}
    return meta.get("infra") or {}


def hotes_du_catalogue() -> list[str]:
    """FQDN de toutes les VM déclarées dans meta.yml."""
    return [h["name"] for h in _infra().get("hosts") or [] if h.get("name")]


def _ip(fqdn: str) -> str:
    """IP de la VM, dérivée comme le fait le Terraform KVM de dsoxlab.

    `cidrhost(cidr, idx + 11)` : l'adresse suit la POSITION de l'hôte dans
    infra.hosts (le meta.yml le rappelle, et interdit d'en insérer au milieu).
    """
    infra = _infra()
    noms = hotes_du_catalogue()
    reseau = ipaddress.ip_network(infra["cidr"])
    return str(reseau.network_address + noms.index(fqdn) + 11)


def hotes_du_lab(lab: Path) -> list[str]:
    """FQDN des VM qu'un lab touche : toutes ses targets, rôles compris.

    Toutes les targets et pas seulement la `default` : un lab multi-distrib
    peut être joué sur Ubuntu, et un reset partiel laisserait l'autre VM sale.
    Rend [] pour un lab shell.
    """
    spec = yaml.safe_load((lab / "lab.yaml").read_text(encoding="utf-8")) or {}
    runtime = spec.get("runtime") or {}
    if runtime.get("type", "shell") == "shell":
        return []
    fqdns: list[str] = []
    if runtime.get("host"):
        fqdns.append(runtime["host"])
    for cible in runtime.get("targets") or []:
        if cible.get("host"):
            fqdns.append(cible["host"])
        fqdns.extend(h for h in (cible.get("roles") or {}).values() if h)
    return list(dict.fromkeys(fqdns))


def _disques(fqdn: str) -> list[str]:
    """Disques inscriptibles du domaine (l'ISO cloud-init est un cdrom, exclu)."""
    res = subprocess.run(
        ["sudo", "virsh", "domblklist", fqdn, "--details"],
        capture_output=True, text=True, check=False,
    )
    disques = []
    for ligne in res.stdout.splitlines():
        champs = ligne.split()
        if len(champs) >= 4 and champs[1] == "disk":
            src = champs[3]
            disques.append(src if src.startswith("/") else str(POOL / src))
    return disques


def _adosse_a(disque: str) -> str | None:
    """Fichier de base (backing file) d'un disque qcow2, ou None."""
    res = subprocess.run(
        ["sudo", "qemu-img", "info", "-U", "--output=json", disque],
        capture_output=True, text=True, check=False,
    )
    if res.returncode != 0:
        return None
    return json.loads(res.stdout).get("full-backing-filename") or json.loads(
        res.stdout
    ).get("backing-filename")


def _base(disque: str) -> str:
    return disque[: -len(".qcow2")] + ".base.qcow2" if disque.endswith(".qcow2") else disque + ".base"


def _golden(fqdn: str) -> str:
    return str(POOL / f"{fqdn}.mem.save")


def _managedsave(fqdn: str) -> str:
    """Là où libvirt attend l'état mémoire d'un domaine PERSISTANT.

    `virsh restore` refuse un domaine persistant (« domain already exists ») :
    on recopie donc le golden ici, et `virsh start` le reprend.
    """
    return f"/var/lib/libvirt/qemu/save/{fqdn}.save"


def _golden_utilisable(fqdn: str) -> bool:
    """Le golden appartient-il au domaine qui porte ce nom AUJOURD'HUI ?

    Un `provision` recrée le domaine sous le même nom avec un UUID neuf, en
    réutilisant les disques : le `.postboot` reste valide, le `.mem.save` est
    mort, et libvirt refuse de le restaurer. La présence des fichiers ne prouve
    donc rien ; on compare les UUID.
    """
    domaine = subprocess.run(
        ["sudo", "virsh", "domuuid", fqdn], capture_output=True, text=True, check=False
    ).stdout.strip()
    dump = subprocess.run(
        ["sudo", "virsh", "save-image-dumpxml", _golden(fqdn)],
        capture_output=True, text=True, check=False,
    )
    trouve = re.search(r"<uuid>([0-9a-f-]+)</uuid>", dump.stdout)
    return bool(domaine) and bool(trouve) and trouve.group(1) == domaine


def _attendre_boot(fqdns: list[str], delai: int = 240) -> list[str]:
    """Attend `systemctl is-system-running` = running/degraded sur chaque VM.

    Le port SSH ne suffit pas : sshd répond bien avant firewalld ou chronyd, et
    un setup joué trop tôt lève. Rend les FQDN qui ne sont jamais revenus.
    """
    absents = []
    for fqdn in fqdns:
        echeance = time.monotonic() + delai
        pret = False
        while time.monotonic() < echeance:
            sonde = subprocess.run(
                ["ssh", "-i", str(CLE_SSH), "-o", "IdentitiesOnly=yes",
                 "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
                 "-o", "LogLevel=ERROR", "-o", "ConnectTimeout=6", "-o", "BatchMode=yes",
                 f"ansible@{_ip(fqdn)}", "systemctl is-system-running 2>/dev/null || true"],
                # stdin fermé : ssh lit sinon l'entrée de l'appelant, et une
                # boucle `while read` qui l'appelle perdait la suite de sa liste.
                stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
            )
            if sonde.stdout.strip() in ("running", "degraded"):
                pret = True
                break
            time.sleep(5)
        if not pret:
            absents.append(fqdn)
    return absents


def _recaler_horloges(fqdns: list[str]) -> None:
    """Pousse l'heure de l'hôte dans chaque VM restaurée.

    L'état mémoire figé ramène l'horloge à l'instant du gel, et chrony n'autorise
    un saut brutal qu'aux trois premières synchronisations après le boot. Un
    certificat, un `at now + 1 hour` ou un journal daté seraient faux d'autant.
    """
    for fqdn in fqdns:
        subprocess.run(
            ["ssh", "-i", str(CLE_SSH), "-o", "IdentitiesOnly=yes",
             "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-o", "LogLevel=ERROR", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
             f"ansible@{_ip(fqdn)}", f"sudo -n date -s @{int(time.time())}"],
            stdin=subprocess.DEVNULL, capture_output=True, timeout=30, check=False,
        )


def snapshot_base(fqdns: list[str]) -> None:
    """Fige la base de chaque VM. À lancer sur des VM FRAÎCHES uniquement.

    La base n'est créée qu'une fois (idempotent) ; l'overlay est toujours remis
    à neuf, pour que l'état figé parte propre.
    """
    for fqdn in fqdns:
        subprocess.run(["sudo", "virsh", "destroy", fqdn], capture_output=True, check=False)
        for disque in _disques(fqdn):
            base = _base(disque)
            # On garde la base seulement si le disque actuel en est DÉJÀ
            # l'overlay (rebase répété). Un `dsoxlab destroy` laisse les
            # `.base.qcow2`, que Terraform ne connaît pas : après un nouveau
            # provision, la réutiliser poserait une base périmée sous un
            # disque neuf. Le disque frais devient alors la base.
            if _adosse_a(disque) != base:
                _run(["sudo", "mv", "-f", disque, base])
            _run(["sudo", "qemu-img", "create", "-f", "qcow2", "-F", "qcow2",
                  "-b", base, disque + ".new"])
            _run(["sudo", "mv", disque + ".new", disque])
        _run(["sudo", "virsh", "pool-refresh", "default"])
        _run(["sudo", "virsh", "start", fqdn])
    absents = _attendre_boot(fqdns)
    if absents:
        raise IsolationEteinte(f"boot non terminé après basing : {', '.join(absents)}")
    # Mémoire et disque figés ENSEMBLE, VM suspendue : les deux sont cohérents.
    for fqdn in fqdns:
        _run(["sudo", "virsh", "managedsave", fqdn])
        _run(["sudo", "cp", _managedsave(fqdn), _golden(fqdn)])
        for disque in _disques(fqdn):
            _run(["sudo", "cp", disque, disque + ".postboot"])
        _run(["sudo", "virsh", "start", fqdn])
    absents = _attendre_boot(fqdns)
    if absents:
        raise IsolationEteinte(f"VM non revenues après le gel : {', '.join(absents)}")


def snapshot_reset(fqdns: list[str]) -> None:
    """Ramène chaque VM à son état figé. Lève si l'une ne peut pas l'être.

    Pas de repli silencieux : une VM sans base ou au golden périmé fait lever
    IsolationEteinte, avec la commande qui répare. Un lab joué sans isolation
    rendrait un verdict qui ne vaut rien, dans un sens comme dans l'autre.
    """
    if not fqdns:
        return
    for fqdn in fqdns:
        disques = _disques(fqdn)
        postboots = [d + ".postboot" for d in disques]
        if not disques or not Path(_golden(fqdn)).exists() or not all(
            Path(p).exists() for p in postboots
        ):
            raise IsolationEteinte(
                f"{fqdn} n'a pas de base figée. Lance `bash scripts/rebase-vms.sh` "
                "sur des VM fraîches (juste après `dsoxlab provision`)."
            )
        if not _golden_utilisable(fqdn):
            raise IsolationEteinte(
                f"{fqdn} : l'état figé appartient à un domaine disparu (un "
                "`provision` a recréé la VM). Détruis, reprovisionne, puis "
                "`bash scripts/rebase-vms.sh`."
            )
    for fqdn in fqdns:
        subprocess.run(["sudo", "virsh", "destroy", fqdn], capture_output=True, check=False)
        for disque in _disques(fqdn):
            _run(["sudo", "cp", disque + ".postboot", disque + ".new"])
            _run(["sudo", "mv", disque + ".new", disque])
        _run(["sudo", "virsh", "pool-refresh", "default"])
        _run(["sudo", "cp", _golden(fqdn), _managedsave(fqdn)])
        _run(["sudo", "virsh", "start", fqdn])
    absents = _attendre_boot(fqdns)
    if absents:
        raise IsolationEteinte(f"VM non revenues après reset : {', '.join(absents)}")
    _recaler_horloges(fqdns)


if __name__ == "__main__":
    # python3 scripts/isolation_vm.py base|reset [fqdn ...]
    action, *cibles = sys.argv[1:] or ["?"]
    cibles = cibles or hotes_du_catalogue()
    if action == "base":
        snapshot_base(cibles)
        perimes = [f for f in cibles if not _golden_utilisable(f)]
        if perimes:
            sys.exit(f"golden toujours périmé pour : {', '.join(perimes)}")
        print(f"base figée et vérifiée : {', '.join(cibles)}")
    elif action == "reset":
        snapshot_reset(cibles)
        print(f"VM ramenées à leur base : {', '.join(cibles)}")
    else:
        sys.exit("usage : isolation_vm.py base|reset [fqdn ...]")
