"""Tests pytest+testinfra : ebpf-durcir-sysctl.

Lab BI-CIBLE : AlmaLinux 10 et Ubuntu 24.04. L'hôte vient de `lab_target_host()`,
donc de `dsoxlab check --target rhel|ubuntu`.

On prouve l'ÉTAT, jamais les commandes tapées :
- les valeurs ACTIVES, lues dans le noyau (`sysctl -n`, en root) ;
- le COMPORTEMENT : un vrai appel système bpf(BPF_MAP_CREATE) lancé par
  l'utilisateur `nobody` doit être refusé avec EPERM ;
- la PERSISTANCE : le test remet lui-même les deux valeurs faibles à chaud,
  rejoue `sysctl --system` (ce que fait le démarrage) et relit. Un réglage posé
  seulement avec `sysctl -w`, ou écrasé par un fichier qui passe après le sien
  (le fichier de debug oublié par le setup), ne survit pas à ce rejeu.

Le test de persistance ne détruit pas le travail de l'apprenant : quelle que
soit l'issue, il remet à chaud les valeurs qui étaient actives avant lui.
"""
from __future__ import annotations

import base64

import pytest

from conftest import lab_host, lab_target_host, message

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")

UNPRIV = "kernel.unprivileged_bpf_disabled"
JIT = "net.core.bpf_jit_harden"

# Appel système bpf(BPF_MAP_CREATE) : 321 sur x86_64, 280 sur aarch64.
# Créer une table de type ARRAY est ce que le noyau autorise à un appelant
# non privilégié quand unprivileged_bpf_disabled vaut 0 ; avec 1 ou 2, il
# répond EPERM. Le programme est envoyé sur l'entrée standard de python3 :
# aucun fichier à poser sur la machine.
SONDE_BPF = """\
import ctypes, errno, os, platform, struct
numeros = {"x86_64": 321, "aarch64": 280}
machine = platform.machine()
if machine not in numeros:
    print("UNSUPPORTED " + machine)
    raise SystemExit(3)
libc = ctypes.CDLL(None, use_errno=True)
attr = ctypes.create_string_buffer(128)
struct.pack_into("IIIII", attr, 0, 2, 4, 4, 1, 0)
retour = libc.syscall(numeros[machine], 0, attr, 128)
if retour >= 0:
    os.close(retour)
    print("CREATED uid=%d" % os.getuid())
else:
    code = ctypes.get_errno()
    print("ERRNO %s %d uid=%d" % (errno.errorcode.get(code, "?"), code, os.getuid()))
"""


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _lire(host, cle: str) -> str:
    """La valeur ACTIVE dans le noyau. Il faut root : `net.core.bpf_jit_harden`
    répond « permission denied » à un utilisateur ordinaire."""
    resultat = host.run(f"sudo -n sysctl -n {cle}")
    assert resultat.rc == 0, message(
        en=f"Cannot read {cle}: {resultat.stderr.strip()}",
        fr=f"Impossible de lire {cle} : {resultat.stderr.strip()}",
    )
    return resultat.stdout.strip()


@pytest.fixture(scope="module")
def apres_rechargement(host):
    """Remet les valeurs faibles à chaud, rejoue `sysctl --system`, relit.

    Rend ce que le noyau a RETENU après le rechargement, puis restaure les
    valeurs qui étaient actives avant le test. Si `unprivileged_bpf_disabled`
    vaut 1, le noyau refuse de le rouvrir : on le note, sans insister.
    """
    avant = {UNPRIV: _lire(host, UNPRIV), JIT: _lire(host, JIT)}
    verrou = avant[UNPRIV] == "1"
    if not verrou:
        host.run(f"sudo -n sysctl -w {UNPRIV}=0")
    host.run(f"sudo -n sysctl -w {JIT}=0")
    rechargement = host.run("sudo -n sysctl --system")
    apres = {UNPRIV: _lire(host, UNPRIV), JIT: _lire(host, JIT)}
    # Ce test ne doit pas défaire le travail : on remet l'état d'avant.
    for cle, valeur in avant.items():
        if apres[cle] != valeur and not (cle == UNPRIV and verrou):
            host.run(f"sudo -n sysctl -w {cle}={valeur}")
    return {"avant": avant, "apres": apres, "rc": rechargement.rc, "verrou": verrou}


def test_ebpf_non_privilegie_desactive(host):
    """`kernel.unprivileged_bpf_disabled` vaut 2 dans le noyau, maintenant."""
    valeur = _lire(host, UNPRIV)
    assert valeur != "1", message(
        en=f"{UNPRIV} is 1: the kernel keeps it locked until the next reboot, "
        "so the lab cannot reset it. The expected value is 2 (same effect for "
        "callers, but reversible). Reboot the VM, then start again.",
        fr=f"{UNPRIV} vaut 1 : le noyau le verrouille jusqu'au prochain "
        "redémarrage, le lab ne pourrait plus le réinitialiser. La valeur "
        "attendue est 2 (même effet pour les appelants, mais réversible). "
        "Redémarre la VM, puis recommence.",
    )
    assert valeur == "2", message(
        en=f"{UNPRIV} is {valeur}: unprivileged users can still call bpf(). "
        "Read the kernel documentation for the meaning of 0, 1 and 2.",
        fr=f"{UNPRIV} vaut {valeur} : un utilisateur sans privilège peut "
        "encore appeler bpf(). La documentation du noyau donne le sens de 0, "
        "1 et 2.",
    )


def test_jit_durci_pour_tous(host):
    """`net.core.bpf_jit_harden` vaut 2 dans le noyau, maintenant."""
    valeur = _lire(host, JIT)
    assert valeur == "2", message(
        en=f"{JIT} is {valeur}. On a server, the hardening must apply to every "
        "program, including those loaded by root: 1 only covers unprivileged "
        "callers, who are already locked out. Read it as root (sudo).",
        fr=f"{JIT} vaut {valeur}. Sur un serveur, le durcissement doit "
        "s'appliquer à tous les programmes, y compris ceux que charge root : "
        "1 ne couvre que les appelants sans privilège, déjà bloqués. Lis la "
        "valeur en root (sudo).",
    )


def test_bpf_refuse_a_un_utilisateur_sans_privilege(host):
    """Comportement : bpf(BPF_MAP_CREATE) lancé par `nobody` rend EPERM."""
    code = base64.b64encode(SONDE_BPF.encode()).decode()
    resultat = host.run(f"echo {code} | base64 -d | sudo -n -u nobody python3 -")
    sortie = resultat.stdout.strip()
    assert not sortie.startswith("UNSUPPORTED"), message(
        en=f"The probe does not support this architecture: {sortie}",
        fr=f"La sonde ne gère pas cette architecture : {sortie}",
    )
    assert sortie.startswith("ERRNO EPERM"), message(
        en="The kernel still lets the unprivileged user 'nobody' create an "
        f"eBPF map (probe says: '{sortie or resultat.stderr.strip()}'). "
        "Expected: the call is refused with EPERM. A value written in a file "
        "is not enough, the running kernel must refuse.",
        fr="Le noyau laisse encore l'utilisateur sans privilège « nobody » "
        f"créer une table eBPF (la sonde répond : « {sortie or resultat.stderr.strip()} »). "
        "Attendu : l'appel est refusé avec EPERM. Une valeur écrite dans un "
        "fichier ne suffit pas, c'est le noyau en marche qui doit refuser.",
    )


def test_jit_durci_persiste(apres_rechargement):
    """Après remise à zéro et `sysctl --system`, le JIT est de nouveau à 2."""
    assert apres_rechargement["rc"] == 0, message(
        en="`sysctl --system` failed: one of the configuration files is "
        "invalid, so nothing is guaranteed at boot.",
        fr="`sysctl --system` a échoué : un fichier de configuration est "
        "invalide, rien n'est garanti au démarrage.",
    )
    valeur = apres_rechargement["apres"][JIT]
    assert valeur == "2", message(
        en=f"After a reload of the sysctl configuration, {JIT} is {valeur}: "
        "the setting only lives in memory. It would be lost at the next boot.",
        fr=f"Après un rechargement de la configuration sysctl, {JIT} vaut "
        f"{valeur} : le réglage ne vit qu'en mémoire. Il serait perdu au "
        "prochain démarrage.",
    )


def test_ebpf_non_privilegie_persiste_malgre_le_fichier_de_debug(apres_rechargement):
    """Après `sysctl --system`, l'eBPF non privilégié est de nouveau fermé (2)."""
    if apres_rechargement["verrou"]:
        pytest.fail(
            message(
                en=f"{UNPRIV} is 1 (locked until reboot): the persistence "
                "cannot be proven. Expected value: 2.",
                fr=f"{UNPRIV} vaut 1 (verrouillé jusqu'au redémarrage) : la "
                "persistance ne peut pas être prouvée. Valeur attendue : 2.",
            )
        )
    valeur = apres_rechargement["apres"][UNPRIV]
    assert valeur == "2", message(
        en=f"After a reload of the sysctl configuration, {UNPRIV} is {valeur}. "
        "Either the setting was never written to a file, or a file read "
        "later puts it back. `sysctl --system` prints every file it reads, "
        "in the order it reads them: the last one to set a key wins.",
        fr=f"Après un rechargement de la configuration sysctl, {UNPRIV} vaut "
        f"{valeur}. Soit le réglage n'a jamais été écrit dans un fichier, soit "
        "un fichier lu plus tard le remet en place. `sysctl --system` affiche "
        "chaque fichier lu, dans l'ordre : le dernier à fixer une clé l'emporte.",
    )
