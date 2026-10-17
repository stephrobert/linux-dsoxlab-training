"""Tests fonctionnels — capstone capstone-serveur-casse.

Sept tests, 100 points. Ils ne demandent JAMAIS comment la panne a été trouvée
ni corrigée : ils constatent l'état observable, depuis l'extérieur quand c'est
l'extérieur qui compte. C'est le principe du capstone, le chemin appartient au
candidat.

Trois d'entre eux sont des GARDE-FOUS, et ils font la valeur de l'épreuve. On
peut toujours faire répondre un site en mettant SELinux en permissive, en
arrêtant le pare-feu et en ouvrant le docroot à tout le monde. Ces trois gestes
« marchent » et sont exactement ce qu'il ne faut pas faire : ils sont notés
zéro ici.

La persistance ne se vérifie pas en redémarrant, comme dans les deux examens
blancs : on contrôle ce qui SURVIVRAIT à un redémarrage. C'est plus sévère pour
le contexte SELinux, parce qu'un `chcon` survit à un reboot mais pas à un
réétiquetage. Seule la règle `semanage fcontext` est durable.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_host_ip, message

SERVEUR = "alma-rhcsa-1.lab"
CLIENT = "alma-rhcsa-2.lab"
DOCROOT = "/srv/site-interne"
MARQUEUR = "CAPSTONE-SERVEUR-CASSE-OK"


@pytest.fixture(scope="module")
def serveur():
    return lab_host(SERVEUR)


@pytest.fixture(scope="module")
def client():
    return lab_host(CLIENT)


@pytest.fixture(scope="module")
def ip_serveur():
    return lab_host_ip(SERVEUR)


@pytest.mark.points(30)
def test_le_site_repond_depuis_le_client(client, ip_serveur):
    """Le verdict, et il se prend DEPUIS LE CLIENT.

    Un `curl localhost` sur le serveur peut rendre 200 alors que personne n'y
    accède : c'est le cas quand nginx n'écoute que sur la boucle locale, quand
    le pare-feu a refermé le port, et c'est le piège du « mais chez moi ça
    marche ». Le seul test qui vaut est celui de l'utilisateur.
    """
    r = client.run(
        f"curl -s -m 10 -o /tmp/page.html -w '%{{http_code}}' http://{ip_serveur}/"
    )
    code = r.stdout.strip()
    assert code == "200", message(
        en=f"The client gets {code or 'no answer'} instead of 200 on "
        f"http://{ip_serveur}/. The site is still down.",
        fr=f"Le client obtient {code or 'aucune réponse'} au lieu de 200 sur "
        f"http://{ip_serveur}/. Le site est toujours en panne.",
    )
    page = client.check_output("cat /tmp/page.html")
    assert MARQUEUR in page, message(
        en="The server answers, but it is not the right page: marker "
        f"{MARQUEUR} is absent. Check the document root being served.",
        fr="Le serveur répond, mais ce n'est pas la bonne page : le marqueur "
        f"{MARQUEUR} est absent. Vérifiez la racine servie.",
    )


@pytest.mark.garde_fou
@pytest.mark.points(10)
def test_nginx_actif_et_persistant(serveur):
    """Actif ne suffit pas : un service non `enabled` ne revient pas au boot."""
    actif = serveur.run("systemctl is-active nginx").stdout.strip()
    assert actif == "active", message(
        en=f"nginx is not active (state: {actif}).",
        fr=f"nginx n'est pas actif (état : {actif}).",
    )

    active_au_boot = serveur.run("systemctl is-enabled nginx").stdout.strip()
    assert active_au_boot == "enabled", message(
        en=f"nginx is `{active_au_boot}`: it would not restart at boot. "
        "The site would go down again at the first reboot.",
        fr=f"nginx est `{active_au_boot}` : il ne redémarrerait pas au boot. "
        "Le site retomberait au premier redémarrage.",
    )


@pytest.mark.garde_fou
@pytest.mark.points(10)
def test_nginx_ecoute_sur_toutes_les_interfaces(serveur, ip_serveur):
    """Le bon port ne suffit pas, il faut la bonne adresse d'écoute.

    Mesure du 2026-09-15, qui a coûté sa valeur à ce test : le serveur par
    défaut livré dans `nginx.conf` écoute sur `[::]:80`, et nginx pose
    `ipv6only=on` sur cette socket. Elle ne sert donc AUCUN client IPv4. Le
    test acceptait cette ligne comme preuve d'écoute réseau, si bien que la
    panne « n'écouter que sur la boucle locale » le passait : le site restait
    injoignable et 10 points étaient acquis.

    On lit maintenant la colonne « Local Address:Port », et on n'accepte que
    ce qu'un client IPv4 peut atteindre.
    """
    ecoutes = serveur.check_output("ss -lnt")
    ouvertes, locales, en_ipv6 = [], [], []
    for ligne in ecoutes.splitlines():
        champs = ligne.split()
        if len(champs) < 5 or champs[0] != "LISTEN":
            continue
        local = champs[3]
        if not local.endswith(":80"):
            continue
        adresse = local.rsplit(":", 1)[0]
        if adresse in ("0.0.0.0", "*") or adresse == ip_serveur:
            ouvertes.append(local)
        elif adresse.startswith("["):
            en_ipv6.append(local)
        else:
            locales.append(local)

    assert ouvertes or locales or en_ipv6, message(
        en="Nothing listens on port 80.",
        fr="Rien n'écoute sur le port 80.",
    )
    assert ouvertes, message(
        en=f"Port 80 is reachable by no IPv4 client: listening on "
        f"{locales + en_ipv6}. A socket on the loopback does not leave "
        "the machine, and the default server's IPv6 socket carries "
        "`ipv6only`, so it does not answer in IPv4 either.\n"
        f"Output of `ss -lnt`:\n{ecoutes}",
        fr=f"Le port 80 n'est joignable par aucun client IPv4 : écoute sur "
        f"{locales + en_ipv6}. Une socket sur la boucle locale ne sort pas de "
        "la machine, et la socket IPv6 du serveur par défaut porte "
        "`ipv6only`, donc elle ne répond pas non plus en IPv4.\n"
        f"Sortie de `ss -lnt` :\n{ecoutes}",
    )


@pytest.mark.garde_fou
@pytest.mark.points(10)
def test_pare_feu_actif_et_port_ouvert(serveur):
    """GARDE-FOU : arrêter firewalld fait « marcher » le site. C'est zéro.

    Un serveur qui répond parce qu'il n'a plus de pare-feu n'est pas réparé,
    il est exposé. La bonne correction ouvre le service, elle ne coupe pas la
    protection.
    """
    actif = serveur.run("systemctl is-active firewalld").stdout.strip()
    assert actif == "active", message(
        en=f"firewalld is `{actif}`. Making the site answer by stopping the "
        "firewall is not a repair: it is a security regression.",
        fr=f"firewalld est `{actif}`. Faire répondre le site en arrêtant le "
        "pare-feu n'est pas une réparation : c'est une régression de sécurité.",
    )
    active_au_boot = serveur.run("systemctl is-enabled firewalld").stdout.strip()
    assert active_au_boot == "enabled", message(
        en=f"firewalld is `{active_au_boot}`: it would not come back at boot.",
        fr=f"firewalld est `{active_au_boot}` : il ne reviendrait pas au boot.",
    )

    permanent = serveur.check_output("firewall-cmd --permanent --list-all")
    # On compare des JETONS, pas des sous-chaînes. Trouvé par red team le
    # 2026-09-15 : un `ports: 8080/tcp` laissé par un autre lab contenait la
    # sous-chaîne « 80/tcp », et le test passait alors qu'aucune règle
    # permanente n'ouvrait le port 80. Une triche `firewall-cmd
    # --add-service=http` sans `--permanent` était donc acceptée.
    def jetons(prefixe: str) -> set[str]:
        for ligne in permanent.splitlines():
            if ligne.strip().startswith(prefixe):
                return set(ligne.split(":", 1)[1].split())
        return set()

    ouvert = "http" in jetons("services:") or "80/tcp" in jetons("ports:")
    assert ouvert, message(
        en="Port 80 is not open PERMANENTLY. An opening "
        "made without `--permanent` disappears at the next reload.\n"
        f"Permanent configuration read:\n{permanent}",
        fr="Le port 80 n'est pas ouvert de façon PERMANENTE. Une ouverture "
        "faite sans `--permanent` disparaît au prochain rechargement.\n"
        f"Configuration permanente lue :\n{permanent}",
    )


@pytest.mark.garde_fou
@pytest.mark.points(15)
def test_selinux_reste_enforcing(serveur):
    """GARDE-FOU : passer SELinux en permissive fait « marcher » le site.

    C'est la réparation à la masse par excellence, celle qu'on trouve en
    premier sur les forums. Elle désarme la protection de toute la machine
    pour un problème de contexte sur un seul répertoire.
    """
    mode = serveur.check_output("getenforce").strip()
    assert mode == "Enforcing", message(
        en=f"SELinux is `{mode}`. The site may answer, but the machine "
        "is no longer protected: that is not the expected fix.",
        fr=f"SELinux est en `{mode}`. Le site répond peut-être, mais la machine "
        "n'est plus protégée : ce n'est pas la correction attendue.",
    )

    config = serveur.file("/etc/selinux/config").content_string
    actives = [
        x.strip() for x in config.splitlines()
        if x.strip().startswith("SELINUX=") and not x.strip().startswith("SELINUXTYPE")
    ]
    assert actives == ["SELINUX=enforcing"], message(
        en=f"/etc/selinux/config carries {actives}: at the next reboot, "
        "SELinux would no longer be enforcing.",
        fr=f"/etc/selinux/config porte {actives} : au prochain redémarrage, "
        "SELinux ne serait plus en enforcing.",
    )


@pytest.mark.garde_fou
@pytest.mark.points(15)
def test_contexte_du_docroot_durable(serveur):
    """Le contexte doit être bon MAINTENANT et le rester après réétiquetage.

    C'est la nuance que ce test existe pour attraper : `chcon` corrige l'état
    courant et survit même à un redémarrage, mais un `restorecon -R /` ou une
    relabellisation au boot le balaie. Seule une règle `semanage fcontext`
    rend la correction durable.
    """
    contexte = serveur.check_output(f"ls -Zd {DOCROOT}")
    assert "httpd_sys_content_t" in contexte, message(
        en=f"The context of {DOCROOT} is `{contexte.split()[0]}`: nginx cannot "
        "read the files there.",
        fr=f"Le contexte de {DOCROOT} est `{contexte.split()[0]}` : nginx ne peut "
        "pas y lire les fichiers.",
    )

    regles = serveur.run(f"semanage fcontext -l | grep -F '{DOCROOT}'").stdout
    assert "httpd_sys_content_t" in regles, message(
        en=f"No `semanage fcontext` rule covers {DOCROOT}. A `chcon` "
        "alone would be erased by the system's first relabelling.",
        fr=f"Aucune règle `semanage fcontext` ne couvre {DOCROOT}. Un `chcon` "
        "seul serait effacé par le premier réétiquetage du système.",
    )

    # Le test qui prouve la durabilité : on réétiquette, et le contexte tient.
    serveur.run(f"restorecon -R {DOCROOT}")
    apres = serveur.check_output(f"ls -Zd {DOCROOT}")
    assert "httpd_sys_content_t" in apres, message(
        en="After `restorecon`, the context fell back: the fix was not "
        "durable.",
        fr="Après `restorecon`, le contexte est retombé : la correction n'était "
        "pas durable.",
    )


@pytest.mark.garde_fou
@pytest.mark.points(10)
def test_docroot_pas_ouvert_a_tout_le_monde(serveur):
    """GARDE-FOU : `chmod -R 777` fait « marcher » le site. C'est zéro.

    Un docroot inscriptible par tous permet à n'importe quel compte de la
    machine de remplacer la page servie.
    """
    mode = serveur.check_output(f"stat -c %a {DOCROOT}").strip()
    assert len(mode) >= 3 and int(mode[-1]) & 0o2 == 0, message(
        en=f"{DOCROOT} is {mode}: it is writable by everyone. "
        "Opening up the permissions is not a repair.",
        fr=f"{DOCROOT} est en {mode} : il est inscriptible par tout le monde. "
        "Ouvrir les droits n'est pas une réparation.",
    )
    page = serveur.check_output(f"stat -c %a {DOCROOT}/index.html").strip()
    assert int(page[-1]) & 0o2 == 0, message(
        en=f"{DOCROOT}/index.html is {page}: anyone can rewrite the "
        "page being served.",
        fr=f"{DOCROOT}/index.html est en {page} : n'importe qui peut réécrire la "
        "page servie.",
    )
