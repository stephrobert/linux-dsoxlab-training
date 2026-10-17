"""Tests pytest+testinfra : ebpf-tracer-bcc.

Lab BI-CIBLE : AlmaLinux 10 (bcc-tools) et Ubuntu 24.04 (bpfcc-tools). L'hôte
vient de `lab_target_host()`, donc de `dsoxlab check --target rhel|ubuntu`.

On prouve l'ÉTAT, jamais les commandes tapées :
- les outils de traçage sont installés ET savent charger un programme eBPF dans
  le noyau (un `--help` ne prouverait rien) ;
- la réponse de l'apprenant (/var/tmp/reponse-ebpf.txt) est comparée à la vérité
  que le setup a tirée au hasard et rangée dans /opt/lab-ebpf/.verite (root,
  0600) : le nom du programme change à chaque `dsoxlab run`, aucune réponse
  ne peut donc être copiée d'une session à l'autre ;
- le garde-fou vérifie que le service mystère n'a été ni redémarré ni modifié :
  on l'observe, on ne le tue pas.
"""
from __future__ import annotations

import posixpath

import pytest

from conftest import lab_host, lab_target_host, message

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")

REPONSE = "/var/tmp/reponse-ebpf.txt"
VERITE = "/opt/lab-ebpf/.verite"
ETAT = "/opt/lab-ebpf/.etat"


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
        "key=value line for 'binaire' and one for 'fichier'.",
        fr=f"{REPONSE} n'existe pas. Écris ta réponse dedans, une ligne "
        "cle=valeur pour « binaire » et une pour « fichier ».",
    )
    return _cles_valeurs(fichier.content_string)


def _outil_bcc_charge_un_programme(host) -> bool:
    """opensnoop tourne une seconde : il compile et charge son programme eBPF."""
    for commande in (
        "/usr/share/bcc/tools/opensnoop",  # AlmaLinux / RHEL
        "opensnoop-bpfcc",  # Ubuntu / Debian
    ):
        if host.run(f"command -v {commande}").rc != 0:
            continue
        if host.run(f"timeout 30 {commande} -d 1").rc == 0:
            return True
    return False


def _bpftrace_charge_un_programme(host) -> bool:
    if host.run("command -v bpftrace").rc != 0:
        return False
    return host.run("timeout 30 bpftrace -e 'BEGIN { exit(); }'").rc == 0


def test_outils_de_tracage_operationnels(host):
    """Une famille d'outils (BCC ou bpftrace) est installée et charge un programme."""
    assert _outil_bcc_charge_un_programme(host) or _bpftrace_charge_un_programme(host), message(
        en="No working tracing tool. Install the BCC tools (bcc-tools on "
        "AlmaLinux, bpfcc-tools on Ubuntu) or bpftrace, then check that one of "
        "them really runs: loading an eBPF program needs root.",
        fr="Aucun outil de traçage opérationnel. Installe les outils BCC "
        "(bcc-tools sur AlmaLinux, bpfcc-tools sur Ubuntu) ou bpftrace, puis "
        "vérifie que l'un d'eux tourne vraiment : charger un programme eBPF "
        "demande root.",
    )


def test_programme_mystere_identifie(host):
    """`binaire=` désigne le programme qui écrit (nom, ou chemin qui finit par le nom)."""
    attendu = _verite(host)["binaire"]
    donne = _reponse(host).get("binaire", "")
    assert donne, message(
        en=f"No 'binaire=' line in {REPONSE}.",
        fr=f"Aucune ligne « binaire= » dans {REPONSE}.",
    )
    assert posixpath.basename(donne) == attendu, message(
        en=f"'{donne}' is not the program that writes the hidden file. "
        "Look at the COMM column of the open() trace, then check the name "
        "against the process itself.",
        fr=f"« {donne} » n'est pas le programme qui écrit dans le fichier caché. "
        "Regarde la colonne COMM de la trace des open(), puis confronte le nom "
        "au processus lui-même.",
    )


def test_fichier_cache_identifie(host):
    """`fichier=` donne le chemin complet du fichier que le programme ouvre."""
    attendu = _verite(host)["fichier"]
    donne = _reponse(host).get("fichier", "")
    assert donne, message(
        en=f"No 'fichier=' line in {REPONSE}.",
        fr=f"Aucune ligne « fichier= » dans {REPONSE}.",
    )
    assert donne == attendu, message(
        en=f"'{donne}' is not the hidden file the program writes to. The "
        "complete path is expected, exactly as the PATH column shows it.",
        fr=f"« {donne} » n'est pas le fichier caché où le programme écrit. "
        "Le chemin complet est attendu, tel que la colonne PATH l'affiche.",
    )


@pytest.mark.garde_fou
def test_service_mystere_intact(host):
    """On observe le service, on ne le tue ni ne le modifie."""
    verite = _verite(host)
    etat = _cles_valeurs(host.file(ETAT).content_string)
    service = host.service("lab-mystere")
    assert service.is_running, message(
        en="The lab-mystere service is no longer running: tracing observes, it "
        "does not kill. Run the lab again (dsoxlab reset).",
        fr="Le service lab-mystere ne tourne plus : le traçage observe, il ne "
        "tue pas. Rejoue le lab (dsoxlab reset).",
    )
    demarrage = host.check_output(
        "systemctl show lab-mystere -p ActiveEnterTimestampMonotonic --value"
    ).strip()
    assert demarrage == etat["demarrage"], message(
        en="The lab-mystere service was restarted. Observe it without "
        "restarting it (dsoxlab reset to start over).",
        fr="Le service lab-mystere a été redémarré. Observe-le sans le "
        "redémarrer (dsoxlab reset pour repartir).",
    )
    programme = f"/usr/local/sbin/{verite['binaire']}"
    empreinte = host.check_output(f"sha256sum {programme}").split()[0]
    assert empreinte == etat["empreinte"], message(
        en="The mystery program was modified.",
        fr="Le programme mystère a été modifié.",
    )
