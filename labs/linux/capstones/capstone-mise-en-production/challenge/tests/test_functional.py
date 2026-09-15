"""Tests fonctionnels — capstone capstone-mise-en-production.

Dix tests, 100 points. Aucun ne demande quelles commandes ont été tapées : ils
lisent l'état observable de la machine, et le dernier la REDÉMARRE avant de
regarder une seconde fois.

Le redémarrage n'est pas décoratif. Une mise en production se juge à ce qui
revient tout seul : un montage absent de fstab, un service non `enabled`, une
règle de pare-feu posée sans `--permanent` ou une étiquette SELinux posée par
`chcon` disparaissent au premier reboot. Ce sont les quatre façons les plus
courantes de livrer un serveur qui marche le jour de la recette et pas le
lendemain.

La seconde validation se prend DEPUIS LE CLIENT, et c'est volontaire : si la
page revient, c'est que le volume s'est remonté, que le service a redémarré,
que le pare-feu a gardé sa règle et que SELinux a gardé ses étiquettes. Un
seul appel couvre les quatre.

Mesure du 2026-09-15, utile à qui reprendra ces tests : testinfra exécute tout
via `sudo`, et le `secure_path` d'AlmaLinux 10 vaut `/sbin:/bin:/usr/sbin:
/usr/bin`. Un faux binaire déposé dans `/usr/local/sbin` pour masquer
`getenforce` ou `firewall-cmd` n'est donc jamais atteint : la triche a été
jouée, elle est inerte.
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
    """Le contenu servi ne doit pas être sur la racine, et le montage doit tenir."""
    monte = serveur.run(f"findmnt -n {DOCROOT}")
    assert monte.rc == 0, (
        f"{DOCROOT} n'est pas un point de montage : le contenu est posé sur la "
        "racine, ce que la consigne d'exploitation interdit."
    )
    assert "vg_app" in monte.stdout or "/dev/mapper/" in monte.stdout, (
        f"{DOCROOT} est monté, mais pas depuis un volume logique : {monte.stdout.strip()}"
    )

    fstab = serveur.file("/etc/fstab").content_string
    lignes = [
        x for x in fstab.splitlines()
        if not x.strip().startswith("#") and len(x.split()) >= 2 and x.split()[1] == DOCROOT
    ]
    assert lignes, (
        f"Aucune entrée fstab pour {DOCROOT} : le volume ne serait pas remonté "
        "au redémarrage."
    )


@pytest.mark.points(10)
def test_le_service_tourne_sous_un_compte_dedie(serveur):
    """Ni root, ni un compte de connexion : un compte système sans shell."""
    compte = serveur.run("id -u cotisation")
    assert compte.rc == 0, "Le compte de service `cotisation` n'existe pas."

    shell = serveur.check_output("getent passwd cotisation").split(":")[-1].strip()
    assert shell in ("/sbin/nologin", "/usr/sbin/nologin", "/bin/false"), (
        f"Le compte de service a `{shell}` comme shell : il peut ouvrir une "
        "session, ce qui n'a pas lieu d'être pour un compte applicatif."
    )

    proprio = serveur.check_output(f"stat -c %U {DOCROOT}").strip()
    assert proprio == "cotisation", (
        f"{DOCROOT} appartient à `{proprio}` et non au compte de service."
    )

    # Le titre de ce test promet que le SERVICE tourne sous un compte dédié.
    # Sans ces lignes, il ne mesurait que l'existence d'un compte et le
    # propriétaire du répertoire : un service laissé sous root marquait les
    # 10 points (red team du 2026-09-15).
    #
    # On exige ce que la consigne exige, ni plus ni moins : « un compte de
    # service, pas root ». Le compte propre à nginx convient, le compte
    # `cotisation` aussi. Le processus maître reste root, c'est sa fonction ;
    # ce sont les workers qui doivent porter un compte non privilégié.
    comptes = set(serveur.run("ps -o user:32= -C nginx").stdout.split())
    travailleurs = comptes - {"root"}
    assert travailleurs, (
        "Tous les processus du service web tournent sous root. La consigne "
        "d'exploitation demande un compte de service : un serveur web qui "
        "sert des fichiers n'a aucun besoin des privilèges de root."
    )
    for nom in sorted(travailleurs):
        ligne = serveur.run(f"getent passwd {nom}").stdout
        shell_worker = ligne.split(":")[-1].strip() if ligne else ""
        assert shell_worker in ("/sbin/nologin", "/usr/sbin/nologin", "/bin/false"), (
            f"Le service tourne sous `{nom}`, dont le shell est "
            f"`{shell_worker or 'inconnu'}` : ce n'est pas un compte de "
            "service, c'est un compte de connexion."
        )


@pytest.mark.points(15)
def test_service_actif_persistant_et_a_l_ecoute(serveur):
    """Actif ne suffit pas : ce qui compte est ce qui revient au boot."""
    actif = serveur.run("systemctl is-active nginx").stdout.strip()
    assert actif == "active", f"Le service web n'est pas actif (état : {actif})."

    au_boot = serveur.run("systemctl is-enabled nginx").stdout.strip()
    assert au_boot == "enabled", (
        f"Le service web est `{au_boot}` : il ne redémarrerait pas au boot."
    )

    # On lit la COLONNE « Local Address:Port », pas la ligne entière. Chercher
    # « 0.0.0.0 » dans la ligne ne mesure rien : la colonne « Peer
    # Address:Port » vaut 0.0.0.0:* sur TOUTE socket IPv4 en écoute, y compris
    # une socket liée à 127.0.0.1. La triche « n'écouter qu'en local »
    # marquait donc les 15 points (red team du 2026-09-15).
    ecoutes = serveur.check_output("ss -lnt")
    ouvert, boucle = [], []
    for ligne in ecoutes.splitlines():
        champs = ligne.split()
        if len(champs) < 5 or champs[0] != "LISTEN":
            continue
        local = champs[3]
        if not local.endswith(f":{PORT}"):
            continue
        adresse = local.rsplit(":", 1)[0]
        (ouvert if adresse in ("0.0.0.0", "*", "[::]") else boucle).append(local)

    assert ouvert, (
        f"Le port {PORT} n'est écouté que sur {boucle} : personne ne peut "
        f"l'atteindre depuis le réseau. Sortie de `ss -lnt` :\n{ecoutes}"
        if boucle else
        f"Rien n'écoute sur le port {PORT} côté réseau. Sortie de `ss -lnt` :\n"
        f"{ecoutes}"
    )


@pytest.mark.points(15)
def test_selinux_enforcing_port_etiquete_et_contexte_durable(serveur):
    """Les trois gestes SELinux d'une mise en production, et leur durabilité.

    Le port 8080 n'appartient PAS à `http_port_t` par défaut sur AlmaLinux 10 :
    sans `semanage port`, le service ne peut pas s'y attacher. Et le contexte du
    contenu doit venir d'une règle `semanage fcontext`, pas d'un `chcon` : le
    test lance `restorecon` avant de conclure, ce qu'un `chcon` ne survit pas.
    """
    mode = serveur.check_output("getenforce").strip()
    assert mode == "Enforcing", (
        f"SELinux est en `{mode}`. Livrer en production avec SELinux désarmé "
        "n'est pas une mise en production."
    )

    ports = serveur.check_output("semanage port -l | grep '^http_port_t'")
    # La sortie liste les ports séparés par des virgules : « 8080, 80, 81 ».
    # Un split sur les espaces seuls rend « 8080, » et le test échouerait sur
    # un état pourtant correct.
    declares = {x.strip(",") for x in ports.replace(",", " ").split()}
    assert str(PORT) in declares, (
        f"Le port {PORT} n'est pas étiqueté `http_port_t` : {ports.strip()}"
    )

    regles = serveur.run(f"semanage fcontext -l | grep -F '{DOCROOT}'").stdout
    assert "httpd_sys_content_t" in regles, (
        f"Aucune règle `semanage fcontext` ne couvre {DOCROOT} : un `chcon` "
        "seul serait effacé au premier réétiquetage."
    )

    serveur.run(f"restorecon -R {DOCROOT}")
    apres = serveur.check_output(f"ls -Zd {DOCROOT}")
    assert "httpd_sys_content_t" in apres, (
        "Après `restorecon`, le contexte est retombé : la correction n'était "
        "pas durable."
    )


@pytest.mark.points(10)
def test_le_pare_feu_ouvre_le_port_de_facon_permanente(serveur):
    """Une règle posée sans --permanent disparaît au premier rechargement."""
    actif = serveur.run("systemctl is-active firewalld").stdout.strip()
    assert actif == "active", (
        f"firewalld est `{actif}`. Rendre le service joignable en arrêtant le "
        "pare-feu n'est pas une livraison, c'est une régression."
    )

    permanent = serveur.check_output("firewall-cmd --permanent --list-all")
    # Comparaison par JETONS, jamais par sous-chaîne. Le même test dans le
    # capstone serveur-casse cherchait « 80/tcp » en sous-chaîne et acceptait
    # un « ports: 8080/tcp » laissé par un autre lab (red team du 2026-09-15).
    # Ici la collision serait « 18080/tcp », qui contient « 8080/tcp ».
    ports = set()
    for ligne in permanent.splitlines():
        if ligne.strip().startswith("ports:"):
            ports = set(ligne.split(":", 1)[1].split())
    assert f"{PORT}/tcp" in ports, (
        f"Le port {PORT}/tcp n'est pas ouvert de façon permanente. Une règle "
        "posée sans `--permanent` disparaît au prochain rechargement.\n"
        f"Configuration permanente lue :\n{permanent}"
    )


@pytest.mark.points(15)
def test_le_client_obtient_la_page(client, ip_serveur):
    """Le verdict, pris comme un utilisateur le prendrait."""
    code, corps = _page(client, ip_serveur)
    assert code == "200", (
        f"Le client obtient {code or 'aucune réponse'} sur "
        f"http://{ip_serveur}:{PORT}/ au lieu de 200."
    )
    assert MARQUEUR in corps, (
        f"Le serveur répond mais ne sert pas la livraison : le marqueur "
        f"{MARQUEUR} est absent."
    )


@pytest.mark.points(5)
def test_le_journal_survit_au_redemarrage(serveur):
    """Sans /var/log/journal, le journal repart de zéro à chaque boot."""
    assert serveur.file("/var/log/journal").is_directory, (
        "/var/log/journal n'existe pas : journald garde tout en mémoire et "
        "perd l'historique au redémarrage, exactement quand on en a besoin."
    )


@pytest.mark.points(5)
def test_sshd_refuse_le_mot_de_passe_et_le_compte_root(serveur):
    """On lit la configuration EFFECTIVE, pas le fichier.

    La machine arrive avec un drop-in permissif dont le nom ne s'annonce pas.
    Ajouter son propre fichier ne suffit donc pas : sshd retient la PREMIÈRE
    valeur lue, et les fichiers sont lus dans l'ordre lexical. C'est tout
    l'intérêt de lire `sshd -T` plutôt que le fichier qu'on vient d'écrire.
    """
    effectif = serveur.check_output("sshd -T").lower()
    assert "passwordauthentication no" in effectif, (
        "sshd accepte encore l'authentification par mot de passe. Vérifiez "
        "avec `sshd -T`, pas avec le fichier que vous venez d'écrire : un "
        "autre drop-in peut gagner."
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

    archives = serveur.run(
        "find /srv/sauvegardes -type f -size +0 2>/dev/null"
    ).stdout.split()
    assert archives, (
        "Aucune archive non vide dans /srv/sauvegardes : la minuterie est en "
        "place mais n'a jamais rien produit. Déclenchez-la une fois pour le "
        "prouver."
    )

    # Une archive qui ne contient pas la livraison n'est pas une sauvegarde.
    # Sans ce contrôle, un `touch /srv/sauvegardes/archive.tar.gz` marquait les
    # 10 points (red team du 2026-09-15). On accepte la copie directe comme
    # l'archive tar, compressée ou non : `tar -xOf` reconnaît gzip, bzip2 et xz.
    contenu = serveur.run(
        f"grep -rqs {MARQUEUR} /srv/sauvegardes && exit 0; "
        "for f in /srv/sauvegardes/*; do "
        f"  tar -xOf \"$f\" 2>/dev/null | grep -q {MARQUEUR} && exit 0; "
        "done; exit 1"
    )
    assert contenu.rc == 0, (
        "Les fichiers de /srv/sauvegardes ne contiennent pas la livraison : "
        f"le marqueur {MARQUEUR} est introuvable, aussi bien en clair que dans "
        "une archive tar. Une sauvegarde qui ne sauvegarde pas le contenu "
        "n'en est pas une."
    )


@pytest.mark.points(10)
def test_tout_revient_apres_un_redemarrage(client, ip_serveur):
    """La seconde validation, celle qui sépare une livraison d'une démonstration.

    On redémarre la machine pour de bon, puis on redemande la page DEPUIS LE
    CLIENT. Si elle revient, c'est que le volume s'est remonté, que le service
    a redémarré seul, que le pare-feu a gardé sa règle et que SELinux a gardé
    ses étiquettes. Un seul appel couvre les quatre oublis les plus courants.
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
        f"Deux minutes après le redémarrage, le client obtient toujours "
        f"{code or 'aucune réponse'}. Quelque chose n'a pas été rendu "
        "persistant : montage, service, pare-feu ou étiquette SELinux."
    )
