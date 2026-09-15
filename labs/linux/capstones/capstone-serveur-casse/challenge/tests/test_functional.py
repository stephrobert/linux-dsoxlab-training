"""Tests fonctionnels — capstone capstone-serveur-casse.

Sept tests, 100 points. Ils ne demandent JAMAIS comment la panne a ete trouvee
ni corrigee : ils constatent l'etat observable, depuis l'exterieur quand c'est
l'exterieur qui compte. C'est le principe du capstone, le chemin appartient au
candidat.

Trois d'entre eux sont des GARDE-FOUS, et ils font la valeur de l'epreuve. On
peut toujours faire repondre un site en mettant SELinux en permissive, en
arretant le pare-feu et en ouvrant le docroot a tout le monde. Ces trois gestes
« marchent » et sont exactement ce qu'il ne faut pas faire : ils sont notes
zero ici.

La persistance ne se verifie pas en redemarrant, comme dans les deux examens
blancs : on controle ce qui SURVIVRAIT a un redemarrage. C'est plus severe pour
le contexte SELinux, parce qu'un `chcon` survit a un reboot mais pas a un
reetiquetage. Seule la regle `semanage fcontext` est durable.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_host_ip

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
    accede : c'est le cas quand nginx n'ecoute que sur la boucle locale, quand
    le pare-feu a referme le port, et c'est le piege du « mais chez moi ca
    marche ». Le seul test qui vaut est celui de l'utilisateur.
    """
    r = client.run(
        f"curl -s -m 10 -o /tmp/page.html -w '%{{http_code}}' http://{ip_serveur}/"
    )
    code = r.stdout.strip()
    assert code == "200", (
        f"Le client obtient {code or 'aucune reponse'} au lieu de 200 sur "
        f"http://{ip_serveur}/. Le site est toujours en panne."
    )
    page = client.check_output("cat /tmp/page.html")
    assert MARQUEUR in page, (
        "Le serveur repond, mais ce n'est pas la bonne page : le marqueur "
        f"{MARQUEUR} est absent. Verifiez la racine servie."
    )


@pytest.mark.points(10)
def test_nginx_actif_et_persistant(serveur):
    """Actif ne suffit pas : un service non `enabled` ne revient pas au boot."""
    actif = serveur.run("systemctl is-active nginx").stdout.strip()
    assert actif == "active", f"nginx n'est pas actif (etat : {actif})."

    active_au_boot = serveur.run("systemctl is-enabled nginx").stdout.strip()
    assert active_au_boot == "enabled", (
        f"nginx est `{active_au_boot}` : il ne redemarrerait pas au boot. "
        "Le site retomberait au premier redemarrage."
    )


@pytest.mark.points(10)
def test_nginx_ecoute_sur_toutes_les_interfaces(serveur):
    """Le bon port ne suffit pas, il faut la bonne adresse d'ecoute."""
    ecoutes = serveur.check_output("ss -lnt")
    lignes = [x for x in ecoutes.splitlines() if ":80 " in x or x.endswith(":80")]
    assert lignes, "Rien n'ecoute sur le port 80."
    locales = [x for x in lignes if "127.0.0.1:80" in x]
    ouvertes = [x for x in lignes if "0.0.0.0:80" in x or "*:80" in x or "[::]:80" in x]
    assert ouvertes, (
        "Le port 80 n'est en ecoute que sur la boucle locale "
        f"({locales}). Depuis le reseau, personne n'y accede."
    )


@pytest.mark.points(10)
def test_pare_feu_actif_et_port_ouvert(serveur):
    """GARDE-FOU : arreter firewalld fait « marcher » le site. C'est zero.

    Un serveur qui repond parce qu'il n'a plus de pare-feu n'est pas repare,
    il est expose. La bonne correction ouvre le service, elle ne coupe pas la
    protection.
    """
    actif = serveur.run("systemctl is-active firewalld").stdout.strip()
    assert actif == "active", (
        f"firewalld est `{actif}`. Faire repondre le site en arretant le "
        "pare-feu n'est pas une reparation : c'est une regression de securite."
    )
    active_au_boot = serveur.run("systemctl is-enabled firewalld").stdout.strip()
    assert active_au_boot == "enabled", (
        f"firewalld est `{active_au_boot}` : il ne reviendrait pas au boot."
    )

    permanent = serveur.check_output("firewall-cmd --permanent --list-all")
    assert "http" in permanent or "80/tcp" in permanent, (
        "Le port 80 n'est pas ouvert de facon PERMANENTE. Une ouverture "
        "faite sans `--permanent` disparait au prochain rechargement."
    )


@pytest.mark.points(15)
def test_selinux_reste_enforcing(serveur):
    """GARDE-FOU : passer SELinux en permissive fait « marcher » le site.

    C'est la reparation a la masse par excellence, celle qu'on trouve en
    premier sur les forums. Elle desarme la protection de toute la machine
    pour un probleme de contexte sur un seul repertoire.
    """
    mode = serveur.check_output("getenforce").strip()
    assert mode == "Enforcing", (
        f"SELinux est en `{mode}`. Le site repond peut-etre, mais la machine "
        "n'est plus protegee : ce n'est pas la correction attendue."
    )

    config = serveur.file("/etc/selinux/config").content_string
    actives = [
        x.strip() for x in config.splitlines()
        if x.strip().startswith("SELINUX=") and not x.strip().startswith("SELINUXTYPE")
    ]
    assert actives == ["SELINUX=enforcing"], (
        f"/etc/selinux/config porte {actives} : au prochain redemarrage, "
        "SELinux ne serait plus en enforcing."
    )


@pytest.mark.points(15)
def test_contexte_du_docroot_durable(serveur):
    """Le contexte doit etre bon MAINTENANT et le rester apres reetiquetage.

    C'est la nuance que ce test existe pour attraper : `chcon` corrige l'etat
    courant et survit meme a un redemarrage, mais un `restorecon -R /` ou une
    relabellisation au boot le balaie. Seule une regle `semanage fcontext`
    rend la correction durable.
    """
    contexte = serveur.check_output(f"ls -Zd {DOCROOT}")
    assert "httpd_sys_content_t" in contexte, (
        f"Le contexte de {DOCROOT} est `{contexte.split()[0]}` : nginx ne peut "
        "pas y lire les fichiers."
    )

    regles = serveur.run(f"semanage fcontext -l | grep -F '{DOCROOT}'").stdout
    assert "httpd_sys_content_t" in regles, (
        f"Aucune regle `semanage fcontext` ne couvre {DOCROOT}. Un `chcon` "
        "seul serait efface par le premier reetiquetage du systeme."
    )

    # Le test qui prouve la durabilite : on reetiquette, et le contexte tient.
    serveur.run(f"restorecon -R {DOCROOT}")
    apres = serveur.check_output(f"ls -Zd {DOCROOT}")
    assert "httpd_sys_content_t" in apres, (
        "Apres `restorecon`, le contexte est retombe : la correction n'etait "
        "pas durable."
    )


@pytest.mark.points(10)
def test_docroot_pas_ouvert_a_tout_le_monde(serveur):
    """GARDE-FOU : `chmod -R 777` fait « marcher » le site. C'est zero.

    Un docroot inscriptible par tous permet a n'importe quel compte de la
    machine de remplacer la page servie.
    """
    mode = serveur.check_output(f"stat -c %a {DOCROOT}").strip()
    assert len(mode) >= 3 and int(mode[-1]) & 0o2 == 0, (
        f"{DOCROOT} est en {mode} : il est inscriptible par tout le monde. "
        "Ouvrir les droits n'est pas une reparation."
    )
    page = serveur.check_output(f"stat -c %a {DOCROOT}/index.html").strip()
    assert int(page[-1]) & 0o2 == 0, (
        f"{DOCROOT}/index.html est en {page} : n'importe qui peut reecrire la "
        "page servie."
    )
