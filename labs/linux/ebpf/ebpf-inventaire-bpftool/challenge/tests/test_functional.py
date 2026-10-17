"""Tests pytest+testinfra : ebpf-inventaire-bpftool.

Lab BI-CIBLE : AlmaLinux 10 et Ubuntu 24.04. L'hôte vient de `lab_target_host()`,
donc de `dsoxlab check --target rhel|ubuntu`.

On prouve l'ÉTAT, jamais les commandes tapées :
- le service porteur est ARRÊTÉ pour de bon : plus de processus, et plus de
  redémarrage automatique (Restart=always) ;
- il ne revient pas au prochain démarrage : l'unité n'est plus `enabled`
  (désactivée, masquée ou retirée) ;
- le noyau ne porte plus le programme eBPF : on interroge `bpftool`, pas
  `systemctl` (retirer le fichier d'une unité en marche ne tue pas le processus) ;
- la réponse (/var/tmp/reponse-inventaire-bpf.txt) est comparée à la vérité que
  le setup a MESURÉE après le chargement du programme (service tiré au hasard,
  type lu dans `bpftool prog show`), rangée dans /opt/lab-ebpf-inventaire/.verite
  (root, 0600) ;
- le garde-fou vérifie que les programmes légitimes du système, relevés à l'état
  initial dans .programmes-legitimes, sont toujours chargés.
"""
from __future__ import annotations

import json

import pytest

from conftest import lab_host, lab_target_host, message

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")

REPONSE = "/var/tmp/reponse-inventaire-bpf.txt"
VERITE = "/opt/lab-ebpf-inventaire/.verite"
LEGITIMES = "/opt/lab-ebpf-inventaire/.programmes-legitimes"

# États de `systemctl is-enabled` qui garantissent que l'unité ne démarrera pas
# toute seule au prochain boot. `masked-runtime` (masquage dans /run) disparaît
# au redémarrage : il n'est donc pas accepté.
ETATS_SANS_RETOUR = {"disabled", "masked", "not-found"}


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def _cles_valeurs(texte: str) -> dict[str, str]:
    """Lignes `cle=valeur` -> dict. Espaces et guillemets autour sont tolérés."""
    resultat: dict[str, str] = {}
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, _, valeur = ligne.partition("=")
        resultat[cle.strip().lower()] = valeur.strip().strip("\"'")
    return resultat


def _verite(host) -> dict[str, str]:
    fichier = host.file(VERITE)
    assert fichier.exists, message(
        en=f"{VERITE} is missing: run the lab setup again (dsoxlab reset).",
        fr=f"{VERITE} est absent : rejoue le setup du lab (dsoxlab reset).",
    )
    return _cles_valeurs(fichier.content_string)


def _reponse(host) -> dict[str, str]:
    fichier = host.file(REPONSE)
    assert fichier.exists, message(
        en=f"{REPONSE} does not exist. Write your answer there, one "
        "key=value line for 'service' and one for 'type'.",
        fr=f"{REPONSE} n'existe pas. Écris ta réponse dedans, une ligne "
        "cle=valeur pour « service » et une pour « type ».",
    )
    return _cles_valeurs(fichier.content_string)


def _json(host, commande: str) -> list[dict]:
    resultat = host.run(commande)
    assert resultat.rc == 0, message(
        en=f"'{commande}' failed: {resultat.stderr.strip()}. bpftool must be "
        "installed and run as root.",
        fr=f"« {commande} » a échoué : {resultat.stderr.strip()}. bpftool doit "
        "être installé et lancé en root.",
    )
    return json.loads(resultat.stdout or "[]")


def _programmes(host) -> list[dict]:
    return _json(host, "bpftool -j prog show")


def _unite(verite: dict[str, str]) -> str:
    return verite["service"]


def _normaliser_service(valeur: str) -> str:
    valeur = valeur.strip()
    return valeur if valeur.endswith(".service") else valeur + ".service"


def test_service_arrete(host):
    """Plus aucun processus du service, et systemd ne le relance pas."""
    unite = _unite(_verite(host))
    etat = _cles_valeurs(
        host.check_output(
            f"systemctl show -p ActiveState -p MainPID {unite}"
        )
    )
    assert etat.get("activestate") not in {"active", "activating", "reloading", "deactivating"}, message(
        en=f"{unite} is still running or being restarted (Restart=always brings a "
        "killed process back). Stop the unit itself, do not kill its process.",
        fr=f"{unite} tourne encore ou est en cours de relance (Restart=always "
        "ramène un processus tué). Arrête l'unité elle-même, pas son processus.",
    )
    assert etat.get("mainpid") == "0", message(
        en=f"{unite} still has a main process.",
        fr=f"{unite} a encore un processus principal.",
    )
    procs = host.run(f"cat /sys/fs/cgroup/system.slice/{unite}/cgroup.procs 2>/dev/null")
    assert not procs.stdout.strip(), message(
        en=f"A process is still running in the cgroup of {unite}. Removing the "
        "unit file does not stop what is already running.",
        fr=f"Un processus tourne encore dans le cgroup de {unite}. Supprimer le "
        "fichier de l'unité n'arrête pas ce qui tourne déjà.",
    )


def test_service_ne_revient_pas_au_demarrage(host):
    """L'unité n'est plus `enabled` : désactivée, masquée ou retirée."""
    unite = _unite(_verite(host))
    etat = host.run(f"systemctl is-enabled {unite}").stdout.strip()
    assert etat in ETATS_SANS_RETOUR, message(
        en=f"{unite} is '{etat}': it would start again at the next boot. "
        "Expected: disabled, masked or removed.",
        fr=f"{unite} est « {etat} » : il redémarrerait au prochain démarrage. "
        "Attendu : désactivé, masqué ou retiré.",
    )


def test_programme_decharge_du_noyau(host):
    """Le noyau ne porte plus le programme de ce type chargé par le service."""
    verite = _verite(host)
    restants = [
        p for p in _programmes(host)
        if p.get("type") == verite["type"]
        and (p.get("name") or "").startswith(verite["programme"])
    ]
    assert not restants, message(
        en="The kernel still holds the program of the service "
        f"({verite['type']} '{verite['programme']}', id "
        f"{', '.join(str(p['id']) for p in restants)}). Ask bpftool, not "
        "systemctl: the program disappears when its process stops.",
        fr="Le noyau porte encore le programme du service "
        f"({verite['type']} « {verite['programme']} », id "
        f"{', '.join(str(p['id']) for p in restants)}). Interroge bpftool, pas "
        "systemctl : le programme disparaît quand son processus s'arrête.",
    )
    sondes = _json(host, "bpftool -j perf show")
    exec_ = [s for s in sondes if s.get("tracepoint") == "sched_process_exec"]
    assert not exec_, message(
        en="A process still holds the sched_process_exec tracepoint probe.",
        fr="Un processus tient encore la sonde du tracepoint sched_process_exec.",
    )


def test_reponse_service(host):
    """`service=` désigne l'unité systemd qui porte le programme."""
    attendu = _unite(_verite(host))
    donne = _reponse(host).get("service", "")
    assert donne, message(
        en=f"No 'service=' line in {REPONSE}.",
        fr=f"Aucune ligne « service= » dans {REPONSE}.",
    )
    assert _normaliser_service(donne) == attendu, message(
        en=f"'{donne}' is not the service that carries the program. Go from the "
        "process that holds the program to its systemd unit.",
        fr=f"« {donne} » n'est pas le service qui porte le programme. Pars du "
        "processus qui tient le programme pour remonter à son unité systemd.",
    )


def test_reponse_type(host):
    """`type=` donne le type du PROGRAMME, tel que `bpftool prog` l'affiche."""
    attendu = _verite(host)["type"]
    donne = _reponse(host).get("type", "")
    assert donne, message(
        en=f"No 'type=' line in {REPONSE}.",
        fr=f"Aucune ligne « type= » dans {REPONSE}.",
    )
    assert donne.lower() == attendu, message(
        en=f"'{donne}' is not the type of the program. Expected: the type of the "
        "PROGRAM as bpftool prog shows it (second field of the first line), not "
        "the type of a link or of a file descriptor.",
        fr=f"« {donne} » n'est pas le type du programme. Attendu : le type du "
        "PROGRAMME tel que bpftool prog l'affiche (deuxième champ de la première "
        "ligne), pas celui d'un lien ou d'un descripteur de fichier.",
    )


@pytest.mark.garde_fou
def test_programmes_legitimes_intacts(host):
    """Les programmes que le système charge (systemd, noyau) sont toujours là."""
    fichier = host.file(LEGITIMES)
    assert fichier.exists, message(
        en=f"{LEGITIMES} is missing: run the lab setup again (dsoxlab reset).",
        fr=f"{LEGITIMES} est absent : rejoue le setup du lab (dsoxlab reset).",
    )
    attendus = {ligne.strip() for ligne in fichier.content_string.splitlines() if ligne.strip()}
    assert attendus, message(
        en="The reference list of legitimate programs is empty.",
        fr="La liste de référence des programmes légitimes est vide.",
    )
    presents = {f"{p['type']} {p.get('name') or '-'}" for p in _programmes(host)}
    manquants = sorted(attendus - presents)
    assert not manquants, message(
        en="Programs the system itself loads have disappeared: "
        f"{', '.join(manquants)}. Only the program of the unknown service must "
        "go. Start again with dsoxlab reset.",
        fr="Des programmes que le système charge lui-même ont disparu : "
        f"{', '.join(manquants)}. Seul le programme du service inconnu doit "
        "partir. Repars avec dsoxlab reset.",
    )
