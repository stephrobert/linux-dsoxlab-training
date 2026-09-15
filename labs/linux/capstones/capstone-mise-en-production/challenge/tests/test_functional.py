"""Tests fonctionnels — capstone capstone-mise-en-production.

Dix tests, 100 points. Aucun ne demande quelles commandes ont ete tapees : ils
lisent l'etat observable de la machine, et le dernier la REDEMARRE avant de
regarder une seconde fois.

Le redemarrage n'est pas decoratif. Une mise en production se juge a ce qui
revient tout seul : un montage absent de fstab, un service non `enabled`, une
regle de pare-feu posee sans `--permanent` ou une etiquette SELinux posee par
`chcon` disparaissent au premier reboot. Ce sont les quatre facons les plus
courantes de livrer un serveur qui marche le jour de la recette et pas le
lendemain.

La seconde validation se prend DEPUIS LE CLIENT, et c'est volontaire : si la
page revient, c'est que le volume s'est remonte, que le service a redemarre,
que le pare-feu a garde sa regle et que SELinux a garde ses etiquettes. Un
seul appel couvre les quatre.
"""
from __future__ import annotations

import time

import pytest

from conftest import lab_host, lab_host_ip

SERVEUR = "alma-rhcsa-1.lab"
CLIENT = "alma-rhcsa-2.lab"
DOCROOT = "/srv/cotisation"
MARQUEUR = "COTISATION-EN-PRODUCTION"
PORT = 8080


@pytest.fixture(scope="module")
def serveur():
    return lab_host(SERVEUR)


@pytest.fixture(scope="module")
def client():
    return lab_host(CLIENT)


@pytest.fixture(scope="module")
def ip_serveur():
    return lab_host_ip(SERVEUR)


def _page(client, ip: str, timeout: int = 10) -> tuple[str, str]:
    """Rend (code HTTP, corps) vus du client."""
    r = client.run(
        f"curl -s -m {timeout} -o /tmp/cotisation.html "
        f"-w '%{{http_code}}' http://{ip}:{PORT}/"
    )
    corps = client.run("cat /tmp/cotisation.html 2>/dev/null").stdout
    return r.stdout.strip(), corps


@pytest.mark.points(15)
def test_le_contenu_vit_sur_un_volume_dedie(serveur):
    """Le contenu servi ne doit pas etre sur la racine, et le montage doit tenir."""
    monte = serveur.run(f"findmnt -n {DOCROOT}")
    assert monte.rc == 0, (
        f"{DOCROOT} n'est pas un point de montage : le contenu est pose sur la "
        "racine, ce que la consigne d'exploitation interdit."
    )
    assert "vg_app" in monte.stdout or "/dev/mapper/" in monte.stdout, (
        f"{DOCROOT} est monte, mais pas depuis un volume logique : {monte.stdout.strip()}"
    )

    fstab = serveur.file("/etc/fstab").content_string
    lignes = [
        x for x in fstab.splitlines()
        if not x.strip().startswith("#") and len(x.split()) >= 2 and x.split()[1] == DOCROOT
    ]
    assert lignes, (
        f"Aucune entree fstab pour {DOCROOT} : le volume ne serait pas remonte "
        "au redemarrage."
    )


@pytest.mark.points(10)
def test_le_service_tourne_sous_un_compte_dedie(serveur):
    """Ni root, ni un compte de connexion : un compte systeme sans shell."""
    compte = serveur.run("id -u cotisation")
    assert compte.rc == 0, "Le compte de service `cotisation` n'existe pas."

    shell = serveur.check_output("getent passwd cotisation").split(":")[-1].strip()
    assert shell in ("/sbin/nologin", "/usr/sbin/nologin", "/bin/false"), (
        f"Le compte de service a `{shell}` comme shell : il peut ouvrir une "
        "session, ce qui n'a pas lieu d'etre pour un compte applicatif."
    )

    proprio = serveur.check_output(f"stat -c %U {DOCROOT}").strip()
    assert proprio == "cotisation", (
        f"{DOCROOT} appartient a `{proprio}` et non au compte de service."
    )


@pytest.mark.points(15)
def test_service_actif_persistant_et_a_l_ecoute(serveur):
    """Actif ne suffit pas : ce qui compte est ce qui revient au boot."""
    actif = serveur.run("systemctl is-active nginx").stdout.strip()
    assert actif == "active", f"Le service web n'est pas actif (etat : {actif})."

    au_boot = serveur.run("systemctl is-enabled nginx").stdout.strip()
    assert au_boot == "enabled", (
        f"Le service web est `{au_boot}` : il ne redemarrerait pas au boot."
    )

    ecoutes = serveur.check_output("ss -lnt")
    ouvert = [
        x for x in ecoutes.splitlines()
        if f":{PORT}" in x and ("0.0.0.0" in x or "*:" in x or "[::]" in x)
    ]
    assert ouvert, (
        f"Rien n'ecoute sur le port {PORT} cote reseau. Sortie de `ss -lnt` :\n"
        f"{ecoutes}"
    )


@pytest.mark.points(15)
def test_selinux_enforcing_port_etiquete_et_contexte_durable(serveur):
    """Les trois gestes SELinux d'une mise en production, et leur durabilite.

    Le port 8080 n'appartient PAS a `http_port_t` par defaut sur AlmaLinux 10 :
    sans `semanage port`, le service ne peut pas s'y attacher. Et le contexte du
    contenu doit venir d'une regle `semanage fcontext`, pas d'un `chcon` : le
    test lance `restorecon` avant de conclure, ce qu'un `chcon` ne survit pas.
    """
    mode = serveur.check_output("getenforce").strip()
    assert mode == "Enforcing", (
        f"SELinux est en `{mode}`. Livrer en production avec SELinux desarme "
        "n'est pas une mise en production."
    )

    ports = serveur.check_output("semanage port -l | grep '^http_port_t'")
    # La sortie liste les ports separes par des virgules : « 8080, 80, 81 ».
    # Un split sur les espaces seuls rend « 8080, » et le test echouerait sur
    # un etat pourtant correct.
    declares = {x.strip(",") for x in ports.replace(",", " ").split()}
    assert str(PORT) in declares, (
        f"Le port {PORT} n'est pas etiquete `http_port_t` : {ports.strip()}"
    )

    regles = serveur.run(f"semanage fcontext -l | grep -F '{DOCROOT}'").stdout
    assert "httpd_sys_content_t" in regles, (
        f"Aucune regle `semanage fcontext` ne couvre {DOCROOT} : un `chcon` "
        "seul serait efface au premier reetiquetage."
    )

    serveur.run(f"restorecon -R {DOCROOT}")
    apres = serveur.check_output(f"ls -Zd {DOCROOT}")
    assert "httpd_sys_content_t" in apres, (
        "Apres `restorecon`, le contexte est retombe : la correction n'etait "
        "pas durable."
    )


@pytest.mark.points(10)
def test_le_pare_feu_ouvre_le_port_de_facon_permanente(serveur):
    """Une regle posee sans --permanent disparait au premier rechargement."""
    actif = serveur.run("systemctl is-active firewalld").stdout.strip()
    assert actif == "active", (
        f"firewalld est `{actif}`. Rendre le service joignable en arretant le "
        "pare-feu n'est pas une livraison, c'est une regression."
    )

    permanent = serveur.check_output("firewall-cmd --permanent --list-all")
    assert f"{PORT}/tcp" in permanent, (
        f"Le port {PORT}/tcp n'est pas ouvert de facon permanente :\n{permanent}"
    )


@pytest.mark.points(15)
def test_le_client_obtient_la_page(client, ip_serveur):
    """Le verdict, pris comme un utilisateur le prendrait."""
    code, corps = _page(client, ip_serveur)
    assert code == "200", (
        f"Le client obtient {code or 'aucune reponse'} sur "
        f"http://{ip_serveur}:{PORT}/ au lieu de 200."
    )
    assert MARQUEUR in corps, (
        f"Le serveur repond mais ne sert pas la livraison : le marqueur "
        f"{MARQUEUR} est absent."
    )


@pytest.mark.points(5)
def test_le_journal_survit_au_redemarrage(serveur):
    """Sans /var/log/journal, le journal repart de zero a chaque boot."""
    assert serveur.file("/var/log/journal").is_directory, (
        "/var/log/journal n'existe pas : journald garde tout en memoire et "
        "perd l'historique au redemarrage, exactement quand on en a besoin."
    )


@pytest.mark.points(5)
def test_sshd_refuse_le_mot_de_passe_et_le_compte_root(serveur):
    """On lit la configuration EFFECTIVE, pas le fichier."""
    effectif = serveur.check_output("sshd -T").lower()
    assert "passwordauthentication no" in effectif, (
        "sshd accepte encore l'authentification par mot de passe."
    )
    assert "permitrootlogin no" in effectif, (
        "sshd accepte encore la connexion directe du compte root."
    )


@pytest.mark.points(10)
def test_la_sauvegarde_est_planifiee_et_a_deja_tourne(serveur):
    """Une sauvegarde qui n'a jamais produit d'archive n'est pas une sauvegarde."""
    actif = serveur.run("systemctl is-active cotisation-sauvegarde.timer").stdout.strip()
    assert actif == "active", (
        f"La minuterie de sauvegarde est `{actif}`."
    )
    au_boot = serveur.run("systemctl is-enabled cotisation-sauvegarde.timer").stdout.strip()
    assert au_boot == "enabled", (
        f"La minuterie est `{au_boot}` : elle ne reviendrait pas au boot."
    )

    archives = serveur.run("ls -1 /srv/sauvegardes/ 2>/dev/null").stdout.split()
    assert archives, (
        "Aucune archive dans /srv/sauvegardes : la minuterie est en place mais "
        "n'a jamais rien produit. Declenchez-la une fois pour le prouver."
    )


@pytest.mark.points(10)
def test_tout_revient_apres_un_redemarrage(client, ip_serveur):
    """La seconde validation, celle qui separe une livraison d'une demonstration.

    On redemarre la machine pour de bon, puis on redemande la page DEPUIS LE
    CLIENT. Si elle revient, c'est que le volume s'est remonte, que le service
    a redemarre seul, que le pare-feu a garde sa regle et que SELinux a garde
    ses etiquettes. Un seul appel couvre les quatre oublis les plus courants.
    """
    serveur = lab_host(SERVEUR)
    serveur.run("nohup sh -c 'sleep 1; systemctl reboot' >/dev/null 2>&1 &")
    time.sleep(15)

    code = ""
    for _ in range(24):
        time.sleep(5)
        code, corps = _page(client, ip_serveur, timeout=4)
        if code == "200" and MARQUEUR in corps:
            return
    pytest.fail(
        f"Deux minutes apres le redemarrage, le client obtient toujours "
        f"{code or 'aucune reponse'}. Quelque chose n'a pas ete rendu "
        "persistant : montage, service, pare-feu ou etiquette SELinux."
    )
