"""Tests fonctionnels — capstone lfcs-mock-exam.

17 tests = 17 tâches de l'examen blanc LFCS. Chaque test est indépendant et
vérifie l'état observable de la VM cible (pas le chemin pris par le candidat).
Pondération via @pytest.mark.points(N) — décoratif pour l'instant, comme dans le
mock RHCSA (dsoxlab calcule passed/total).

Cible : ubuntu-lfcs-1.lab (les 17 tâches, 5 domaines LFCS).

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le solution.yaml
chiffré du formateur avant les tests (mode CI) — c'est ce qui prouve que les 17
tâches sont réalisables. En `dsoxlab check`, elle est désactivée
(LAB_NO_REPLAY=1) : les tests notent le travail du candidat.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET = "ubuntu-lfcs-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET)


def _fstab_line(host, mount: str) -> str | None:
    """Retourne la ligne fstab qui monte `mount`, sinon None."""
    for line in host.file("/etc/fstab").content_string.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2 and fields[1] == mount:
            return stripped
    return None


# ======================================================================
# Section A — Essential Commands (20 pts)
# ======================================================================


@pytest.mark.points(5)
def test_task01_git_repository(host):
    """Dépôt Git initialisé, deux fichiers commités, .cache ignoré, branche recette.

    Objectif LFCS : « Basic Git Operations ». Le test interroge Git, pas le
    disque : un .git recopie a la main ne rend pas un journal de commits.
    """
    depot = "/srv/deploiement"
    dans_depot = host.run(f"git -C {depot} rev-parse --is-inside-work-tree")
    assert dans_depot.rc == 0 and dans_depot.stdout.strip() == "true", message(
        en=f"{depot} is not a Git repository.",
        fr=f"{depot} n'est pas un dépôt Git.",
    )

    commits = host.run(f"git -C {depot} rev-list --count HEAD")
    assert commits.rc == 0 and int(commits.stdout.strip() or 0) >= 1, message(
        en="No commit in the repository: initialising is not enough.",
        fr="Aucun commit dans le dépôt : initialiser ne suffit pas.",
    )

    suivis = set(host.check_output(f"git -C {depot} ls-files").split())
    assert {"config.yml", "notes.txt"} <= suivis, message(
        en=f"config.yml and notes.txt must be tracked (tracked: {sorted(suivis)}).",
        fr=f"config.yml et notes.txt doivent être suivis (suivis : {sorted(suivis)}).",
    )
    intrus = [f for f in suivis if f.startswith(".cache/")]
    assert not intrus, message(
        en=f".cache/ must not be versioned, yet it is: {intrus}",
        fr=f".cache/ ne doit pas être versionné, or il l'est : {intrus}",
    )

    etat = host.check_output(f"git -C {depot} status --porcelain")
    assert ".cache" not in etat, message(
        en="git status still mentions .cache: it is not ignored.\n"
        f"{etat}",
        fr="git status mentionne encore .cache : il n'est pas ignoré.\n"
        f"{etat}",
    )

    # `branch --list recette` plutot qu'un format personnalise : testinfra
    # n'applique le formatage % que si on lui passe des arguments, un
    # --format=%(refname:short) arriverait donc tel quel ou mal echappe.
    recette = host.run(f"git -C {depot} branch --list recette")
    assert recette.rc == 0 and recette.stdout.strip(), message(
        en="The recette branch is missing.\n"
        + host.check_output(f"git -C {depot} branch -a"),
        fr="La branche recette est absente.\n"
        + host.check_output(f"git -C {depot} branch -a"),
    )


@pytest.mark.points(6)
def test_task02_broken_service_repaired(host):
    """collecteur.service repare : actif, active au boot, et il ecrit vraiment.

    Objectif LFCS : « Create, configure, and troubleshoot services ». Deux
    défauts sont posés par le setup, un ExecStart qui ne pointe nulle part et
    un script prive de son bit d'execution. Le test ne dit pas comment les
    corriger, il constate que le service tourne et produit.
    """
    svc = host.service("collecteur")
    assert svc.is_running, message(
        en="collecteur.service is not active. `systemctl status collecteur` and "
        "`journalctl -u collecteur` name both faults.",
        fr="collecteur.service n'est pas actif. `systemctl status collecteur` et "
        "`journalctl -u collecteur` nomment les deux défauts.",
    )
    assert svc.is_enabled, message(
        en="collecteur.service is not enabled at boot.",
        fr="collecteur.service n'est pas active au boot.",
    )

    journal = host.file("/var/log/collecteur.log")
    assert journal.exists, message(
        en="/var/log/collecteur.log does not exist.",
        fr="/var/log/collecteur.log n'existe pas.",
    )
    assert journal.size > 0, message(
        en="/var/log/collecteur.log is empty: is the service really running, "
        "or was it started just now without ever writing?",
        fr="/var/log/collecteur.log est vide : le service tourne-t-il vraiment, "
        "ou a-t-il été démarré à l'instant sans jamais écrire ?",
    )


@pytest.mark.points(4)
def test_task03_deleted_file_space_released(host):
    """L'unité fautive est nommée, arrêtée, et l'espace est rendu.

    Objectif LFCS : « Troubleshoot diskspace issues ». Le cas est celui qui
    coute le plus de temps en production : df compte l'espace, du ne le trouve
    pas, parce qu'un processus retient un fichier déjà supprimé.
    """
    reponse = host.file("/root/diskspace.txt")
    assert reponse.exists, message(
        en="/root/diskspace.txt is missing.",
        fr="/root/diskspace.txt est absent.",
    )
    assert "fuite-disque" in reponse.content_string, message(
        en="The file must name the unit responsible. Seen: "
        f"{reponse.content_string.strip()!r}",
        fr="Le fichier doit nommer l'unité responsable. Vu : "
        f"{reponse.content_string.strip()!r}",
    )

    svc = host.service("fuite-disque")
    assert not svc.is_running, message(
        en="fuite-disque.service is still running.",
        fr="fuite-disque.service tourne encore.",
    )
    assert not svc.is_enabled, message(
        en="fuite-disque.service will come back at boot: it must be disabled too.",
        fr="fuite-disque.service reviendra au boot : il faut aussi le désactiver.",
    )

    # La preuve par l'espace : plus aucun fichier supprimé de cette taille
    # n'est retenu ouvert. lsof +L1 ne liste que les fichiers sans lien.
    retenus = host.run(
        "lsof -nP +L1 2>/dev/null | awk '$8+0 > 100000000 {print $1, $8}'"
    )
    assert not retenus.stdout.strip(), message(
        en="A process still holds a large deleted file:\n"
        f"{retenus.stdout}",
        fr="Un processus retient encore un gros fichier supprimé :\n"
        f"{retenus.stdout}",
    )


@pytest.mark.points(5)
def test_task04_self_signed_certificate(host):
    """Certificat auto-signé, CN attendu, 365 jours, clé privée protégée.

    Objectif LFCS : « Work with SSL certificates ». Le test verifie aussi que
    la cle correspond au certificat : deux fichiers generes separement passent
    tous les controles de forme et ne servent a rien ensemble.
    """
    cle = host.file("/etc/ssl/lab/collecteur.key")
    cert = host.file("/etc/ssl/lab/collecteur.crt")
    assert cle.exists, message(
        en="/etc/ssl/lab/collecteur.key is missing.",
        fr="/etc/ssl/lab/collecteur.key est absent.",
    )
    assert cert.exists, message(
        en="/etc/ssl/lab/collecteur.crt is missing.",
        fr="/etc/ssl/lab/collecteur.crt est absent.",
    )

    assert cle.mode & 0o077 == 0, message(
        en="The private key must stay readable by root alone "
        f"(mode seen: {oct(cle.mode)}).",
        fr="La clé privée doit rester lisible par root seul "
        f"(mode vu : {oct(cle.mode)}).",
    )

    sujet = host.run("openssl x509 -noout -subject -in /etc/ssl/lab/collecteur.crt")
    assert sujet.rc == 0, message(
        en=f"The certificate cannot be read:\n{sujet.stderr}",
        fr=f"Le certificat ne se lit pas :\n{sujet.stderr}",
    )
    assert "collecteur.lab" in sujet.stdout, message(
        en=f"CN collecteur.lab expected, seen: {sujet.stdout.strip()}",
        fr=f"CN attendu collecteur.lab, vu : {sujet.stdout.strip()}",
    )

    # 364 jours et non 365 : le certificat est emis le jour meme, exiger
    # exactement 365 ferait echouer un travail correct a quelques heures pres.
    validite = host.run(
        f"openssl x509 -noout -checkend {364 * 86400} "
        "-in /etc/ssl/lab/collecteur.crt"
    )
    assert validite.rc == 0, message(
        en="The certificate expires in less than 365 days.",
        fr="Le certificat expire dans moins de 365 jours.",
    )

    mod_cert = host.check_output(
        "openssl x509 -noout -modulus -in /etc/ssl/lab/collecteur.crt "
        "2>/dev/null | openssl md5"
    )
    mod_cle = host.check_output(
        "openssl rsa -noout -modulus -in /etc/ssl/lab/collecteur.key "
        "2>/dev/null | openssl md5"
    )
    assert mod_cert == mod_cle, message(
        en="The private key does not match the certificate: they were not "
        "generated for one another.",
        fr="La clé privée ne correspond pas au certificat : ils n'ont pas été "
        "générés l'un pour l'autre.",
    )


# ======================================================================
# Section B — Operations Deployment (25 pts)
# ======================================================================


@pytest.mark.points(5)
def test_task05_package_installed_and_held(host):
    """tree doit être installé ET gelé (hold)."""
    assert host.package("tree").is_installed, message(
        en="The tree package is not installed.",
        fr="Le paquet tree n'est pas installé.",
    )
    holds = host.check_output("apt-mark showhold")
    assert "tree" in holds.split(), message(
        en="tree is not on hold: an upgrade could move it. "
        f"Seen: {holds!r}",
        fr="tree n'est pas en hold : une mise à jour pourrait le bouger. "
        f"Vu : {holds!r}",
    )


@pytest.mark.points(7)
def test_task06_service_unit(host):
    """labwatch.service doit être activé (boot) et démarré (maintenant)."""
    svc = host.service("labwatch")
    assert svc.is_enabled, message(
        en="labwatch.service is not enabled: it would not come back at reboot.",
        fr="labwatch.service n'est pas enabled : il ne reviendrait pas au reboot.",
    )
    assert svc.is_running, message(
        en="labwatch.service is not started.",
        fr="labwatch.service n'est pas démarré.",
    )


@pytest.mark.points(7)
def test_task07_timer(host):
    """labreport.timer : activé, actif, déclenchement quotidien à 03:00."""
    timer = host.service("labreport.timer")
    assert timer.is_enabled, message(
        en="labreport.timer is not enabled.",
        fr="labreport.timer n'est pas enabled.",
    )
    assert timer.is_running, message(
        en="labreport.timer is not active.",
        fr="labreport.timer n'est pas actif.",
    )
    cal = host.check_output(
        "systemctl show labreport.timer --property=TimersCalendar"
    )
    assert "03:00" in cal, message(
        en=f"The timer must fire at 03:00 (OnCalendar). Seen: {cal!r}",
        fr=f"Le timer doit se déclencher à 03:00 (OnCalendar). Vu : {cal!r}",
    )
    unit = host.file("/etc/systemd/system/labreport.service")
    assert unit.exists, message(
        en="The labreport.service unit is missing.",
        fr="L'unité labreport.service est absente.",
    )
    assert "labreport.sh" in unit.content_string, message(
        en="labreport.service must run /usr/local/bin/labreport.sh.",
        fr="labreport.service doit exécuter /usr/local/bin/labreport.sh.",
    )


@pytest.mark.points(6)
def test_task08_cron(host):
    """devops doit avoir une entrée cron toutes les 10 minutes."""
    cron = host.check_output("crontab -u devops -l 2>/dev/null || true")
    assert "labreport.sh" in cron, message(
        en=f"No cron job for devops calls labreport.sh. Seen: {cron!r}",
        fr=f"Aucune tâche cron pour devops n'appelle labreport.sh. Vu : {cron!r}",
    )
    ligne = next(
        (ligne for ligne in cron.splitlines()
         if "labreport.sh" in ligne and not ligne.strip().startswith("#")),
        "",
    )
    assert ligne.split()[0] == "*/10", message(
        en="The job must run every 10 minutes (*/10 in the minute field). "
        f"Seen: {ligne!r}",
        fr="La tâche doit tourner toutes les 10 minutes (*/10 en champ minute). "
        f"Vu : {ligne!r}",
    )


# ======================================================================
# Section C — Users and Groups (10 pts)
# ======================================================================


@pytest.mark.points(5)
def test_task09_account(host):
    """auditor1 : UID 3001, shell bash, membre du groupe auditors."""
    u = host.user("auditor1")
    assert u.exists, message(
        en="User auditor1 does not exist.",
        fr="L'utilisateur auditor1 n'existe pas.",
    )
    assert u.uid == 3001, message(
        en=f"auditor1's UID must be 3001 (seen: {u.uid}).",
        fr=f"L'UID d'auditor1 doit être 3001 (vu : {u.uid}).",
    )
    assert u.shell == "/bin/bash", message(
        en=f"auditor1's shell must be /bin/bash (seen: {u.shell}).",
        fr=f"Le shell d'auditor1 doit être /bin/bash (vu : {u.shell}).",
    )
    assert "auditors" in u.groups, message(
        en=f"auditor1 must be a member of the auditors group (seen: {u.groups}).",
        fr=f"auditor1 doit être membre du groupe auditors (vu : {u.groups}).",
    )


@pytest.mark.points(5)
def test_task10_acl_on_reports_directory(host):
    """ACL POSIX sur /srv/rapports, y compris l'ACL par défaut.

    Objectif LFCS : « Configure and manage ACLs ». Le répertoire est à
    root:root en 0750 : sans ACL, devops n'entre pas. Le test verifie aussi que
    le mode standard n'a pas bougé, parce qu'un chmod 0757 donnerait l'accès
    sans repondre a l'objectif, et ouvrirait a tout le monde au passage.
    """
    d = host.file("/srv/rapports")
    assert d.exists and d.is_directory, message(
        en="/srv/rapports does not exist.",
        fr="/srv/rapports n'existe pas.",
    )
    assert d.user == "root" and d.group == "root", message(
        en=f"The owner was not to change (seen: {d.user}:{d.group}).",
        fr=f"Le propriétaire ne devait pas changer (vu : {d.user}:{d.group}).",
    )
    # Les bits de GROUPE ne sont volontairement pas testes : des qu'une entree
    # nommée existe, POSIX place un MASQUE dans l'ACL, et c'est ce masque que
    # stat affiche a la place des droits de groupe. Un 0750 devient 0770 sans
    # qu'aucun chmod n'ait été tapé. Ce qui doit rester vrai, c'est que rien
    # n'a été ouvert au reste du monde et que le propriétaire garde la main.
    assert d.mode & 0o007 == 0, message(
        en="The directory has become accessible to everyone. The access asked for "
        f"goes through a named ACL, not through a chmod (seen: {oct(d.mode)}).",
        fr="Le répertoire est devenu accessible à tout le monde. L'accès demandé "
        f"passe par une ACL nommée, pas par un chmod (vu : {oct(d.mode)}).",
    )
    assert (d.mode >> 6) & 0o7 == 0o7, message(
        en=f"root lost rights on its own directory (seen: {oct(d.mode)}).",
        fr=f"root a perdu des droits sur son propre répertoire (vu : {oct(d.mode)}).",
    )

    # `-p` seul : `-pn` afficherait les identifiants numeriques et aucune
    # comparaison sur le nom « devops » ne pourrait aboutir.
    acl_rep = host.check_output("getfacl -p /srv/rapports 2>/dev/null")
    assert "user:devops:rwx" in acl_rep, message(
        en=f"devops does not have rwx on /srv/rapports:\n{acl_rep}",
        fr=f"devops n'a pas rwx sur /srv/rapports :\n{acl_rep}",
    )
    defaut = [l for l in acl_rep.splitlines() if l.startswith("default:user:devops:")]
    assert defaut, message(
        en="No default ACL for devops: new files will inherit "
        f"nothing.\n{acl_rep}",
        fr="Aucune ACL par défaut pour devops : les nouveaux fichiers n'hériteront "
        f"de rien.\n{acl_rep}",
    )
    droits_defaut = defaut[0].rsplit(":", 1)[-1]
    assert "r" in droits_defaut and "w" in droits_defaut, message(
        en=f"The default ACL must grant at least rw (seen: {defaut[0]}).",
        fr=f"L'ACL par défaut doit accorder au moins rw (vue : {defaut[0]}).",
    )

    acl_fic = host.check_output("getfacl -p /srv/rapports/bilan.csv 2>/dev/null")
    assert "user:devops:rw" in acl_fic, message(
        en="devops does not have rw on the file already present: a default ACL "
        f"is not retroactive, what already exists must be handled too.\n{acl_fic}",
        fr="devops n'a pas rw sur le fichier déjà présent : une ACL par défaut "
        f"n'est pas rétroactive, il faut aussi traiter l'existant.\n{acl_fic}",
    )

    # Preuve par l'usage : un fichier cree maintenant doit hériter de l'ACL.
    host.check_output("rm -f /srv/rapports/.sonde-acl")
    host.check_output("touch /srv/rapports/.sonde-acl")
    herite = host.check_output("getfacl -p /srv/rapports/.sonde-acl 2>/dev/null")
    host.check_output("rm -f /srv/rapports/.sonde-acl")
    assert "user:devops:rw" in herite, message(
        en="A file created just now does not grant rw to devops: the default "
        f"ACL has no effect.\n{herite}",
        fr="Un fichier créé à l'instant n'accorde pas rw à devops : l'ACL par "
        f"défaut ne produit pas son effet.\n{herite}",
    )


# ======================================================================
# Section D — Networking (25 pts)
# ======================================================================


@pytest.mark.points(8)
def test_task11_static_ip(host):
    """lab0 doit porter 198.51.100.10 en live, et le déclarer dans netplan."""
    addr = host.check_output("ip -4 addr show lab0")
    assert "198.51.100.10" in addr, message(
        en=f"lab0 does not carry 198.51.100.10 live. Seen:\n{addr}",
        fr=f"lab0 ne porte pas 198.51.100.10 en live. Vu :\n{addr}",
    )
    conf = host.check_output(
        "grep -rl 198.51.100.10 /etc/netplan/ 2>/dev/null || true"
    )
    assert conf.strip(), message(
        en="No file in /etc/netplan/ declares 198.51.100.10: the address "
        "would be lost at reboot.",
        fr="Aucun fichier /etc/netplan/ ne déclare 198.51.100.10 : l'adresse "
        "serait perdue au reboot.",
    )


@pytest.mark.points(5)
def test_task12_static_route(host):
    """La route vers 203.0.113.0/24 doit être active ET déclarée dans netplan.

    La consigne dit « toujours avec netplan » : sans la seconde moitié de ce
    test, un `ip route add` marquait les 5 points et la route disparaissait au
    premier redémarrage (red team du 2026-09-15). Le test de l'adresse
    statique, juste au-dessus, contrôlait déjà les deux.
    """
    routes = host.check_output("ip route show")
    assert "203.0.113.0/24" in routes, message(
        en=f"The route to 203.0.113.0/24 is missing. Seen:\n{routes}",
        fr=f"La route vers 203.0.113.0/24 est absente. Vu :\n{routes}",
    )
    conf = host.check_output(
        "grep -rl '203\\.0\\.113\\.0/24' /etc/netplan/ 2>/dev/null || true"
    )
    assert conf.strip(), message(
        en="No file in /etc/netplan/ declares the route to 203.0.113.0/24: "
        "it was set by hand and would be lost at reboot.",
        fr="Aucun fichier /etc/netplan/ ne déclare la route vers 203.0.113.0/24 : "
        "elle a été posée à la main et serait perdue au reboot.",
    )


@pytest.mark.points(7)
def test_task13_firewall(host):
    """ufw actif, 8080/tcp autorisé, SSH toujours ouvert."""
    status = host.check_output("ufw status")
    assert "Status: active" in status, message(
        en=f"ufw is not active. Seen:\n{status}",
        fr=f"ufw n'est pas actif. Vu :\n{status}",
    )
    # Comparaison par jetons : « 8080/tcp » se trouve aussi dans « 18080/tcp »,
    # qu'une autre règle pourrait avoir ouvert.
    assert "8080/tcp" in status.split(), message(
        en=f"Port 8080/tcp is not allowed. Seen:\n{status}",
        fr=f"Le port 8080/tcp n'est pas autorisé. Vu :\n{status}",
    )
    assert "OpenSSH" in status or "22/tcp" in status, message(
        en=f"SSH must stay allowed. Seen:\n{status}",
        fr=f"SSH doit rester autorisé. Vu :\n{status}",
    )


@pytest.mark.points(5)
def test_task14_name_resolution(host):
    """lab-target.lab doit résoudre localement vers 198.51.100.10."""
    out = host.check_output("getent hosts lab-target.lab || true")
    assert "198.51.100.10" in out, message(
        en="The name lab-target.lab does not resolve to 198.51.100.10 "
        f"(/etc/hosts). Seen: {out!r}",
        fr="Le nom lab-target.lab ne résout pas vers 198.51.100.10 "
        f"(/etc/hosts). Vu : {out!r}",
    )


# ======================================================================
# Section E — Storage (20 pts)
# ======================================================================


@pytest.mark.points(8)
def test_task15_lvm_mount_by_uuid(host):
    """vgdata/lvapp en XFS monté sur /data, persistant PAR UUID."""
    assert host.mount_point("/data").exists, message(
        en="/data is not mounted.",
        fr="/data n'est pas monté.",
    )
    source, fstype = host.check_output("findmnt -no SOURCE,FSTYPE /data").split()
    assert "vgdata" in source and "lvapp" in source, message(
        en=f"/data must be mounted from the LV vgdata/lvapp (seen: {source}).",
        fr=f"/data doit être monté depuis le LV vgdata/lvapp (vu : {source}).",
    )
    assert fstype == "xfs", message(
        en=f"/data must be XFS (seen: {fstype}).",
        fr=f"/data doit être en XFS (vu : {fstype}).",
    )
    ligne = _fstab_line(host, "/data")
    assert ligne is not None, message(
        en="No fstab entry for /data: the mount would be lost at reboot.",
        fr="Aucune entrée fstab pour /data : le montage serait perdu au reboot.",
    )
    assert ligne.split()[0].startswith("UUID="), message(
        en="The fstab entry for /data must reference the filesystem by "
        f"UUID=, not by device path. Seen: {ligne!r}",
        fr="L'entrée fstab de /data doit référencer le système de fichiers par "
        f"UUID=, pas par chemin de device. Vu : {ligne!r}",
    )


@pytest.mark.points(7)
def test_task16_automount_on_demand(host):
    """/mnt/auto/donnees monte a la demande par autofs, et absent de fstab.

    Objectif LFCS : « Configure filesystem automounters ». Le quota, teste ici
    auparavant, ne figure dans aucun objectif LFCS.
    """
    svc = host.service("autofs")
    assert svc.is_running, message(
        en="The autofs service is not active.",
        fr="Le service autofs n'est pas actif.",
    )
    assert svc.is_enabled, message(
        en="The autofs service is not enabled at boot.",
        fr="Le service autofs n'est pas active au boot.",
    )

    ligne = _fstab_line(host, "/mnt/auto/donnees")
    assert ligne is None, message(
        en="/mnt/auto/donnees is mounted through /etc/fstab. The exam asks for an "
        f"on-demand mount, not a mount at boot:\n{ligne}",
        fr="/mnt/auto/donnees est monté par /etc/fstab. L'epreuve demande un "
        f"montage a la demande, pas un montage au boot :\n{ligne}",
    )

    # Le seul controle qui prouve l'automontage : y acceder declenche le
    # montage. On demonte d'abord pour ne pas mesurer un reste du run precedent.
    host.run("umount /mnt/auto/donnees 2>/dev/null")
    acces = host.run("ls /mnt/auto/donnees")
    assert acces.rc == 0, message(
        en="Accessing /mnt/auto/donnees fails: the automounter does not know "
        f"that key.\n{acces.stderr}",
        fr="L'accès à /mnt/auto/donnees échoue : l'automonteur ne connaît pas "
        f"cette cle.\n{acces.stderr}",
    )

    fstype = host.run("findmnt -no FSTYPE /mnt/auto/donnees")
    assert fstype.rc == 0 and fstype.stdout.strip() == "xfs", message(
        en="After access, /mnt/auto/donnees must be mounted as XFS "
        f"(seen: {fstype.stdout.strip()!r}).",
        fr="Après accès, /mnt/auto/donnees doit être monté en XFS "
        f"(vu : {fstype.stdout.strip()!r}).",
    )


@pytest.mark.points(5)
def test_task17_swapfile(host):
    """/swapfile de 256 Mio, actif et persistant."""
    swaps = host.check_output("swapon --show=NAME,SIZE --noheadings || true")
    assert "/swapfile" in swaps, message(
        en=f"/swapfile is not an active swap. Seen: {swaps!r}",
        fr=f"/swapfile n'est pas un swap actif. Vu : {swaps!r}",
    )
    taille = host.check_output("stat -c %%s %s", "/swapfile")
    mio = int(taille) // (1024 * 1024)
    assert 250 <= mio <= 262, message(
        en=f"/swapfile must be about 256 MiB (seen: {mio} MiB).",
        fr=f"/swapfile doit faire ~256 Mio (vu : {mio} Mio).",
    )
    # Le swap ne se cherche pas comme un montage : la ligne canonique est
    # « /swapfile none swap sw 0 0 » — le 2e champ vaut none, pas swap.
    ligne = next(
        (entree for entree in host.file("/etc/fstab").content_string.splitlines()
         if "/swapfile" in entree and not entree.strip().startswith("#")),
        None,
    )
    assert ligne is not None, message(
        en="No fstab entry for /swapfile: the swap would be lost at reboot. "
        "Expected: /swapfile none swap sw 0 0",
        fr="Aucune entrée fstab pour /swapfile : le swap serait perdu au reboot. "
        "Attendu : /swapfile none swap sw 0 0",
    )
    assert "swap" in ligne.split(), message(
        en=f"The fstab entry for /swapfile must be of type swap. Seen: {ligne!r}",
        fr=f"L'entrée fstab de /swapfile doit être de type swap. Vu : {ligne!r}",
    )
