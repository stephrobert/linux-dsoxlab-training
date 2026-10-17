"""Tests fonctionnels — capstone rhcsa-mock-exam.

20 tests = 20 tâches du capstone EX200 mock. Chaque test est indépendant
et vérifie l'état observable de la VM cible (pas le chemin pris par
l'apprenant). Pondération via @pytest.mark.points(N) — pour l'instant
décoratif (dsoxlab calcule passed/total), mais sera consommé quand on
ajoutera le plugin pytest-points dans dsoxlab.

Cibles testées :
- alma-rhcsa-1.lab (15 tâches : storage, script shell, services, SELinux…)
- alma-rhcsa-2.lab (5 tâches : NFS mount, client de temps, SSH key auth,
  IP statique, root reset)

Deux compétences ne sont PAS notées ici parce qu'elles ne figurent pas au
référentiel EX200 : exporter un partage NFS et configurer un serveur de temps.
Les deux sont fournies par setup.yaml, et seul leur versant client est noté.

Le module conftest.py racine du repo expose ``lab_host(name)`` qui
retourne un host testinfra connecté en SSH+sudo via le ssh_config
OpenSSH généré par dsoxlab (cf. dsoxlab.infra.inventory.write_ssh_config).
"""

from __future__ import annotations

import re

import pytest

from conftest import lab_host, lab_host_ip, message

SRV1 = "alma-rhcsa-1.lab"
SRV2 = "alma-rhcsa-2.lab"


@pytest.fixture(scope="module")
def srv1():
    return lab_host(SRV1)


@pytest.fixture(scope="module")
def srv2():
    return lab_host(SRV2)


# ── Section A — Stockage et systèmes de fichiers ────────────────────────────

@pytest.mark.points(4)
def test_01_partition_gpt_vdb(srv1):
    """Tâche 1 : /dev/vdb a une table GPT et 2 partitions ~4 GiB."""
    out = srv1.run("parted -s /dev/vdb print")
    assert out.rc == 0, message(
        en=f"parted /dev/vdb failed: {out.stderr}",
        fr=f"parted /dev/vdb échoue : {out.stderr}",
    )
    assert "gpt" in out.stdout.lower(), message(
        en="A GPT partition table is expected on /dev/vdb",
        fr="Table de partitions GPT attendue sur /dev/vdb",
    )
    # 2 partitions visibles
    parts = re.findall(r"^\s*(\d+)\s+", out.stdout, re.MULTILINE)
    assert len(parts) >= 2, message(
        en=f"At least 2 partitions expected, found: {len(parts)}",
        fr=f"Au moins 2 partitions attendues, trouvé : {len(parts)}",
    )


@pytest.mark.points(6)
def test_02_lvm_lvdata_mounted_on_data(srv1):
    """Tâche 2 : VG vgapp + LV lvdata 3 GiB XFS monté sur /data via UUID au boot."""
    # VG existe
    vg = srv1.run("vgs --noheadings -o vg_name vgapp")
    assert vg.rc == 0 and "vgapp" in vg.stdout, message(
        en="VG vgapp missing",
        fr="VG vgapp absent",
    )
    # LV existe avec ~3 GiB initial (peut avoir été étendu dans tâche 3)
    lv = srv1.run("lvs --noheadings -o lv_name vgapp/lvdata")
    assert lv.rc == 0 and "lvdata" in lv.stdout, message(
        en="LV lvdata missing",
        fr="LV lvdata absent",
    )
    # Monté sur /data en XFS
    mp = srv1.mount_point("/data")
    assert mp.exists, message(
        en="/data is not a mount point",
        fr="/data n'est pas un point de montage",
    )
    assert mp.filesystem == "xfs", message(
        en=f"Filesystem xfs expected, found {mp.filesystem}",
        fr=f"FS attendu xfs, trouvé {mp.filesystem}",
    )
    # Persistant via UUID dans /etc/fstab (pas par chemin /dev/...)
    fstab = srv1.file("/etc/fstab").content_string
    assert re.search(r"^UUID=\S+\s+/data\s+xfs", fstab, re.MULTILINE), message(
        en="The /data mount must be declared in /etc/fstab by UUID, as XFS",
        fr="Le mount /data doit être déclaré dans /etc/fstab par UUID en XFS",
    )


@pytest.mark.points(5)
def test_03_lvdata_extended_to_3_5g(srv1):
    """Tâche 3 : lvdata étendu à 3.5 GiB et XFS reflète la nouvelle taille."""
    lv = srv1.run("lvs --noheadings --units g -o lv_size vgapp/lvdata")
    assert lv.rc == 0, message(
        en=f"Cannot read the size of vgapp/lvdata: {lv.stderr.strip()}",
        fr=f"Impossible de lire la taille de vgapp/lvdata : {lv.stderr.strip()}",
    )
    size = float(lv.stdout.strip().rstrip("g").replace(",", "."))
    assert size >= 3.45, message(
        en=f"lvdata must be at least 3.5 GiB, found {size}",
        fr=f"lvdata doit faire au moins 3.5 GiB, trouvé {size}",
    )
    # XFS résolu : df -h /data doit montrer ~3.5G aussi
    df = srv1.run("df -BG --output=size /data | tail -1")
    df_size = int(df.stdout.strip().rstrip("G"))
    assert df_size >= 3, message(
        en=f"XFS on /data must reflect the extension: {df_size}G",
        fr=f"XFS sur /data doit refléter l'extension : {df_size}G",
    )


@pytest.mark.points(4)
def test_04_swapfile_active_persistent(srv1):
    """Tâche 4 : /swapfile 512 MiB activé et persistant via fstab."""
    f = srv1.file("/swapfile")
    assert f.exists, message(
        en="/swapfile missing",
        fr="/swapfile manquant",
    )
    assert f.size >= 500 * 1024 * 1024, message(
        en=f"Size too small: {f.size} bytes",
        fr=f"Taille trop petite : {f.size} bytes",
    )
    # Active
    swap = srv1.run("swapon --show=NAME --noheadings")
    # Comparaison ligne à ligne : « /swapfile » se trouve aussi dans un
    # « /swapfile2 » resté d'un autre essai.
    actifs = [x.strip() for x in swap.stdout.splitlines() if x.strip()]
    assert "/swapfile" in actifs, message(
        en=f"/swapfile not activated through swapon. Active swaps: {actifs or 'none'}",
        fr=f"/swapfile pas activé via swapon. Swaps actifs : {actifs or 'aucun'}",
    )
    # Persistant
    fstab = srv1.file("/etc/fstab").content_string
    assert re.search(r"^/swapfile\s+\S+\s+swap", fstab, re.MULTILINE), message(
        en="/swapfile absent from /etc/fstab",
        fr="/swapfile absent de /etc/fstab",
    )


# ── Section A bis — Script shell ───────────────────────────────────────────

@pytest.mark.points(6)
def test_05_rapport_groupe_script(srv1):
    """Tâche 5 : /usr/local/bin/rapport-groupe.sh, jugé sur son comportement.

    Les quatre objectifs EX200 de « Create simple shell scripts » sont couverts
    par ce seul script : traitement de $1, exécution conditionnelle, boucle sur
    les membres du groupe, et exploitation de la sortie d'une commande.

    Le test n'ouvre jamais le script : il l'exécute. Imposer `getent` plutôt
    que `id`, ou `[` plutôt que `[[`, reviendrait à noter une méthode alors que
    l'examen note un résultat.
    """
    script = srv1.file("/usr/local/bin/rapport-groupe.sh")
    assert script.exists, message(
        en="/usr/local/bin/rapport-groupe.sh is missing",
        fr="/usr/local/bin/rapport-groupe.sh est absent",
    )
    assert script.mode & 0o111, message(
        en=f"The script is not executable (mode {oct(script.mode)})",
        fr=f"Le script n'est pas exécutable (mode {oct(script.mode)})",
    )

    # Sans argument : code 2, rien sur stdout.
    vide = srv1.run("/usr/local/bin/rapport-groupe.sh")
    assert vide.rc == 2, message(
        en=f"With no argument, exit code 2 expected, got {vide.rc}",
        fr=f"Sans argument, code de retour attendu 2, obtenu {vide.rc}",
    )
    assert vide.stdout.strip() == "", message(
        en=f"With no argument, standard output must stay empty: {vide.stdout!r}",
        fr=f"Sans argument, la sortie standard doit rester vide : {vide.stdout!r}",
    )

    # Groupe inconnu : code 3, rien sur stdout.
    inconnu = srv1.run("/usr/local/bin/rapport-groupe.sh groupe-qui-nexiste-pas")
    assert inconnu.rc == 3, message(
        en=f"Unknown group, exit code 3 expected, got {inconnu.rc}",
        fr=f"Groupe inconnu, code de retour attendu 3, obtenu {inconnu.rc}",
    )
    assert inconnu.stdout.strip() == "", message(
        en=f"Unknown group, standard output must stay empty: {inconnu.stdout!r}",
        fr=f"Groupe inconnu, la sortie standard doit rester vide : {inconnu.stdout!r}",
    )

    # Groupe existant : une ligne par membre, verdict conforme au disque.
    res = srv1.run("/usr/local/bin/rapport-groupe.sh evaluation")
    assert res.rc == 0, message(
        en=f"On an existing group, exit code 0 expected, got {res.rc}",
        fr=f"Sur un groupe existant, code de retour attendu 0, obtenu {res.rc}",
    )
    lignes = {ligne.strip() for ligne in res.stdout.splitlines() if ligne.strip()}
    attendu = {"eva-jean:OK", "eva-marie:OK", "eva-paul:ABSENT"}
    assert lignes == attendu, message(
        en="The report does not match the state of the home directories.\n"
        f"  expected: {sorted(attendu)}\n"
        f"  got     : {sorted(lignes)}",
        fr="Le rapport ne correspond pas à l'état des répertoires personnels.\n"
        f"  attendu : {sorted(attendu)}\n"
        f"  obtenu  : {sorted(lignes)}",
    )


# ── Section B — Utilisateurs, groupes, permissions ──────────────────────────

@pytest.mark.points(5)
def test_06_appuser_uid_password_aging(srv1):
    """Tâche 6 : appuser UID 1500, max 60j, warn 7j."""
    u = srv1.user("appuser")
    assert u.exists, message(
        en="appuser missing",
        fr="appuser absent",
    )
    assert u.uid == 1500, message(
        en=f"UID 1500 expected, found {u.uid}",
        fr=f"UID attendu 1500, trouvé {u.uid}",
    )
    assert u.shell == "/bin/bash", message(
        en=f"appuser's shell must be /bin/bash (seen: {u.shell})",
        fr=f"Le shell d'appuser doit être /bin/bash (vu : {u.shell})",
    )
    chage = srv1.run("chage -l appuser")
    assert "Maximum number of days between password change\t: 60" in chage.stdout or \
           re.search(r"Maximum.*:\s*60", chage.stdout), message(
        en="Max age != 60",
        fr="Max age != 60",
    )
    assert re.search(r"warning.*:\s*7", chage.stdout, re.IGNORECASE), message(
        en="Warn != 7",
        fr="Warn != 7",
    )


@pytest.mark.points(5)
def test_07_developers_group_and_shared_dir(srv1):
    """Tâche 7 : groupe developers GID 2000 + /srv/shared setgid."""
    g = srv1.group("developers")
    assert g.exists, message(
        en="group developers missing",
        fr="groupe developers absent",
    )
    assert g.gid == 2000, message(
        en=f"GID 2000 expected, found {g.gid}",
        fr=f"GID attendu 2000, trouvé {g.gid}",
    )
    assert "appuser" in g.members and "devuser" in g.members, message(
        en="appuser and devuser must be in developers",
        fr="appuser et devuser doivent être dans developers",
    )
    d = srv1.file("/srv/shared")
    assert d.is_directory, message(
        en="/srv/shared missing",
        fr="/srv/shared absent",
    )
    assert d.group == "developers", message(
        en=f"group developers expected, found {d.group}",
        fr=f"group attendu developers, trouvé {d.group}",
    )
    # Setgid + 775
    mode = int(srv1.run("stat -c %a /srv/shared").stdout.strip(), 8)
    assert mode == 0o2775, message(
        en=f"Mode 2775 expected (setgid+775), found {oct(mode)}",
        fr=f"Mode attendu 2775 (setgid+775), trouvé {oct(mode)}",
    )


@pytest.mark.points(4)
def test_08_acl_appuser_on_myapp_log(srv1):
    """Tâche 8 : ACL user:appuser:rwx sur /var/log/myapp.log."""
    assert srv1.file("/var/log/myapp.log").exists, message(
        en="/var/log/myapp.log missing",
        fr="/var/log/myapp.log manquant",
    )
    acl = srv1.run("getfacl --absolute-names /var/log/myapp.log")
    assert "user:appuser:rwx" in acl.stdout, message(
        en=f"ACL user:appuser:rwx missing:\n{acl.stdout}",
        fr=f"ACL user:appuser:rwx absente :\n{acl.stdout}",
    )


# ── Section C — Réseau ──────────────────────────────────────────────────────

def _mgmt_connection(host) -> str:
    """Nom de la connexion NetworkManager qui porte l'accès de gestion.

    Jamais codé en dur : le nom du profil et du device varient selon l'image et
    le provider (ici « cloud-init eth0 » sur eth0, mais rien ne le garantit).
    On identifie la connexion par sa FONCTION : celle qui porte la route par
    défaut.
    """
    dev = host.check_output("ip route | awk '/^default/ {print $5; exit}'")
    return host.check_output(
        "nmcli -t -f NAME,DEVICE con show --active "
        "| awk -F: -v d=%s '$2==d {print $1; exit}'",
        dev,
    )


def _assert_static_pinned(host, fqdn: str) -> None:
    """Vérifie que la config réseau est FIGÉE en statique, sans avoir bougé.

    C'est le vrai geste RHCSA : passer la connexion de DHCP (auto) à statique
    (manual), en déclarant adresse, passerelle et DNS de façon permanente.

    L'adresse attendue est celle de l'INVENTORY, et c'est délibéré : exiger une
    adresse différente couperait la session SSH par laquelle testinfra note le
    candidat — il perdrait les 20 tâches d'un coup. Le piège d'examen n'est pas
    « quelle adresse », c'est la MÉTHODE et la PERSISTANCE.
    """
    con = _mgmt_connection(host)
    assert con, message(
        en="No NetworkManager connection carries the default route.",
        fr="Aucune connexion NetworkManager ne porte la route par défaut.",
    )

    methode = host.check_output("nmcli -g ipv4.method con show %s", con)
    assert methode == "manual", message(
        en="The management connection is still on DHCP: it must be pinned to "
        f"static (ipv4.method manual). Seen: {methode!r}.",
        fr="La connexion de gestion est encore en DHCP : elle doit être figée en "
        f"statique (ipv4.method manual). Vu : {methode!r}.",
    )

    attendu = lab_host_ip(fqdn)
    adresses = host.check_output("nmcli -g ipv4.addresses con show %s", con)
    assert attendu in adresses, message(
        en=f"The connection must declare address {attendu}/24, the machine's "
        f"own, to be kept. Seen: {adresses!r}.",
        fr=f"La connexion doit déclarer l'adresse {attendu}/24 — celle de la "
        f"machine, à conserver. Vu : {adresses!r}.",
    )

    passerelle = host.check_output("nmcli -g ipv4.gateway con show %s", con)
    assert passerelle == "10.10.30.1", message(
        en=f"The gateway must be declared (10.10.30.1). Seen: {passerelle!r}.",
        fr=f"La passerelle doit être déclarée (10.10.30.1). Vu : {passerelle!r}.",
    )

    dns = host.check_output("nmcli -g ipv4.dns con show %s", con)
    assert "10.10.30.1" in dns, message(
        en="The network's DNS (10.10.30.1) must be declared: it is what "
        "resolves the .lab names. Declaring a public resolver instead breaks "
        f"the NFS mount by name of task 18. Seen: {dns!r}.",
        fr="Le DNS du réseau (10.10.30.1) doit être déclaré : c'est lui qui "
        "résout les noms .lab. Déclarer un résolveur public à sa place casse "
        f"le montage NFS par nom de la tâche 18. Vu : {dns!r}.",
    )

    # L'adresse doit être RÉELLEMENT portée : un profil modifié mais jamais
    # appliqué ne compte pas.
    live = host.check_output("ip -4 addr show")
    assert attendu in live, message(
        en=f"Address {attendu} is not active: the profile was modified but "
        "not applied (nmcli con up).",
        fr=f"L'adresse {attendu} n'est pas active : le profil a été modifié mais "
        "pas appliqué (nmcli con up).",
    )


@pytest.mark.points(6)
def test_09_srv1_static_ip_hostname_firewall_8080(srv1):
    """Tâche 9 : srv-1 réseau figé en statique, hostname, port 8080/tcp."""
    _assert_static_pinned(srv1, SRV1)
    hn = srv1.run("hostnamectl --static")
    assert hn.stdout.strip() == "srv-rhcsa-1.lab", message(
        en=f"Static hostname: {hn.stdout}",
        fr=f"Hostname static : {hn.stdout}",
    )
    fw = srv1.run("firewall-cmd --list-ports --permanent")
    # Comparaison par JETONS. Cherchée en sous-chaîne, « 8080/tcp » serait
    # trouvée dans un « 18080/tcp » ouvert pour tout autre chose : le candidat
    # marquerait les 6 points sans avoir ouvert le bon port (red team du
    # 2026-09-15, même défaut relevé sur les deux capstones).
    assert "8080/tcp" in fw.stdout.split(), message(
        en=f"Port 8080/tcp not permanently open. Ports read: {fw.stdout.strip() or 'none'}",
        fr=f"Port 8080/tcp pas ouvert permanent. Ports lus : {fw.stdout.strip() or 'aucun'}",
    )


@pytest.mark.points(4)
def test_17_srv2_static_ip_hostname(srv2):
    """Tâche 17 : srv-2 réseau figé en statique + hostname srv-rhcsa-2.lab."""
    _assert_static_pinned(srv2, SRV2)
    hn = srv2.run("hostnamectl --static")
    assert hn.stdout.strip() == "srv-rhcsa-2.lab", message(
        en=f"Static hostname: {hn.stdout}",
        fr=f"Hostname static : {hn.stdout}",
    )


# ── Section D — Services ───────────────────────────────────────────────────

@pytest.mark.points(5)
def test_10_myapp_service_running(srv1):
    """Tâche 10 : myapp.service actif, activé au boot, Restart=on-failure."""
    svc = srv1.service("myapp")
    assert svc.is_running, message(
        en="myapp.service not active",
        fr="myapp.service pas actif",
    )
    assert svc.is_enabled, message(
        en="myapp.service not enabled at boot",
        fr="myapp.service pas activé au boot",
    )
    unit = srv1.file("/etc/systemd/system/myapp.service").content_string
    assert "Restart=on-failure" in unit, message(
        en="Restart=on-failure missing",
        fr="Restart=on-failure manquant",
    )
    assert "ExecStart=/usr/local/bin/myapp.sh" in unit, message(
        en="ExecStart incorrect",
        fr="ExecStart incorrect",
    )
    assert "User=appuser" in unit, message(
        en="User=appuser missing",
        fr="User=appuser manquant",
    )


@pytest.mark.points(4)
def test_11_weekly_backup_timer(srv1):
    """Tâche 11 : weekly-backup.timer dimanche 03:00, actif et activé."""
    timer = srv1.run("systemctl is-active weekly-backup.timer")
    assert timer.stdout.strip() == "active", message(
        en="Timer not active",
        fr="Timer pas actif",
    )
    enabled = srv1.run("systemctl is-enabled weekly-backup.timer")
    assert enabled.stdout.strip() == "enabled", message(
        en="Timer not enabled at boot",
        fr="Timer pas activé au boot",
    )
    show = srv1.run("systemctl cat weekly-backup.timer")
    assert re.search(r"OnCalendar=.*Sun.*03:00", show.stdout), message(
        en="OnCalendar must target Sunday 03:00",
        fr="OnCalendar doit cibler dimanche 03:00",
    )


@pytest.mark.points(4)
def test_12_srv2_time_client_uses_srv1(srv2):
    """Tâche 12 : srv-2 se synchronise sur srv-1.

    L'objectif EX200 dit « Configure time service clients ». Le serveur de
    temps est donc un donné du lab, posé par setup.yaml sur srv-1, et c'est la
    configuration cliente qui est notée ici.
    """
    srv1_ip = lab_host_ip(SRV1)
    conf = srv2.file("/etc/chrony.conf").content_string
    source = re.search(
        rf"^\s*(server|pool)\s+(alma-rhcsa-1\S*|{re.escape(srv1_ip)})\b",
        conf,
        re.MULTILINE,
    )
    assert source, message(
        en="No time source pointing at srv-1 in /etc/chrony.conf "
        f"(expected 'server alma-rhcsa-1.lab' or 'server {srv1_ip}')",
        fr="Aucune source de temps pointant srv-1 dans /etc/chrony.conf "
        f"(attendu 'server alma-rhcsa-1.lab' ou 'server {srv1_ip}')",
    )

    svc = srv2.service("chronyd")
    assert svc.is_running, message(
        en="chronyd is not active on srv-2",
        fr="chronyd n'est pas actif sur srv-2",
    )
    assert svc.is_enabled, message(
        en="chronyd is not enabled at boot on srv-2",
        fr="chronyd n'est pas activé au boot sur srv-2",
    )

    # La configuration doit être chargée, pas seulement écrite : chronyc
    # interroge le démon vivant, un fichier jamais relu ne passe pas.
    sources = srv2.run("chronyc -n sources")
    assert sources.rc == 0, message(
        en=f"chronyc sources failed:\n{sources.stderr}",
        fr=f"chronyc sources a échoué :\n{sources.stderr}",
    )
    assert srv1_ip in sources.stdout, message(
        en=f"srv-1 ({srv1_ip}) does not appear in chronyc sources. "
        "Was the daemon reloaded after the file was modified?\n"
        f"{sources.stdout}",
        fr=f"srv-1 ({srv1_ip}) n'apparaît pas dans chronyc sources. "
        "Le démon a-t-il été rechargé après modification du fichier ?\n"
        f"{sources.stdout}",
    )


# ── Section E — SELinux ────────────────────────────────────────────────────

@pytest.mark.points(4)
def test_13_restorecon_index_html(srv1):
    """Tâche 13 : /var/www/html/index.html a le contexte httpd_sys_content_t."""
    out = srv1.run("ls -Z /var/www/html/index.html")
    assert "httpd_sys_content_t" in out.stdout, message(
        en=f"SELinux context not restored:\n{out.stdout}",
        fr=f"Contexte SELinux pas restauré :\n{out.stdout}",
    )


@pytest.mark.points(5)
def test_14_selinux_boolean_httpd_can_network_connect(srv1):
    """Tâche 14 : boolean httpd_can_network_connect=on permanent."""
    out = srv1.run("getsebool httpd_can_network_connect")
    assert "--> on" in out.stdout, message(
        en=f"Boolean not enabled: {out.stdout}",
        fr=f"Boolean pas activé : {out.stdout}",
    )
    # Vérifier persistance : semanage boolean -l doit afficher "on" en colonne default
    perm = srv1.run("semanage boolean -l | grep httpd_can_network_connect")
    # Format : "name (on , on) Description" → 2e champ = persistant
    assert re.search(r"\bon\s*,\s*on\b", perm.stdout), message(
        en=f"Boolean not persistent: {perm.stdout}",
        fr=f"Boolean pas persistant : {perm.stdout}",
    )


@pytest.mark.points(5)
def test_15_selinux_port_label_8888_http(srv1):
    """Tâche 15 : port 8888/tcp étiqueté http_port_t."""
    out = srv1.run("semanage port -l")
    found = re.search(r"http_port_t\s+tcp\s+([\d, ]+)", out.stdout)
    assert found, message(
        en="http_port_t absent from semanage port",
        fr="http_port_t absent de semanage port",
    )
    ports = [p.strip() for p in found.group(1).split(",")]
    assert "8888" in ports, message(
        en=f"Port 8888 not listed under http_port_t: {ports}",
        fr=f"Port 8888 pas listé sous http_port_t : {ports}",
    )


# ── Section F — Stockage réseau client ─────────────────────────────────────

@pytest.mark.points(6)
def test_18_srv2_nfs_mount(srv2):
    """Tâche 18 : srv-2 monte alma-rhcsa-1.lab:/srv/nfs-public sur /mnt/share."""
    mp = srv2.mount_point("/mnt/share")
    assert mp.exists, message(
        en="/mnt/share is not a mount point",
        fr="/mnt/share n'est pas un point de montage",
    )
    assert mp.filesystem in ("nfs", "nfs4"), message(
        en=f"Filesystem nfs expected, found {mp.filesystem}",
        fr=f"FS attendu nfs, trouvé {mp.filesystem}",
    )
    fstab = srv2.file("/etc/fstab").content_string
    assert re.search(
        r"alma-rhcsa-1\.lab:/srv/nfs-public\s+/mnt/share\s+nfs",
        fstab,
    ), message(
        en="NFS mount absent from /etc/fstab",
        fr="Mount NFS absent de /etc/fstab",
    )
    assert "_netdev" in fstab, message(
        en="Option _netdev missing",
        fr="Option _netdev manquante",
    )


# ── Section G — SSH cross-host et boot recovery ────────────────────────────

@pytest.mark.points(7)
def test_19_ssh_key_auth_srv2_to_srv1(srv2):
    """Tâche 19 : SSH key-only srv-2 → srv-1 et password désactivé sur srv-2."""
    # Test login key-only depuis srv-2 vers srv-1 (BatchMode = échoue si prompt)
    srv1_ip = lab_host_ip(SRV1)
    out = srv2.run(
        "sudo -u appuser ssh -o BatchMode=yes -o StrictHostKeyChecking=no "
        "-o UserKnownHostsFile=/dev/null appuser@%s hostname",
        srv1_ip,
    )
    assert out.rc == 0, message(
        en=f"SSH key authentication fails: {out.stderr}",
        fr=f"SSH key auth échoue : {out.stderr}",
    )
    assert "srv-rhcsa-1" in out.stdout, message(
        en=f"Unexpected hostname: {out.stdout}",
        fr=f"Hostname inattendu : {out.stdout}",
    )
    # PasswordAuthentication désactivé sur srv-2
    sshd = srv2.run("sshd -T 2>/dev/null | grep -i passwordauthentication")
    assert "passwordauthentication no" in sshd.stdout.lower(), message(
        en=f"PasswordAuthentication must be disabled: {sshd.stdout}",
        fr=f"PasswordAuthentication doit être désactivé : {sshd.stdout}",
    )


@pytest.mark.points(6)
def test_20_root_password_reset_srv2(srv2):
    """Tâche 20 : le mot de passe root de srv-2 est bien SecureP@ss2026!.

    On recalcule le hash avec le MÊME sel ET le même algorithme, puis on
    compare. `crypt.crypt(mdp, hash)` réutilise le préfixe du hash fourni, donc
    ça marche pour $6$ comme pour $y$ (yescrypt, le défaut d'AlmaLinux 10).

    L'ancienne version tentait `openssl passwd -6`, qui ne sait pas reproduire
    un $y$, puis retombait sur `echo mdp | su - root -c whoami` — or les tests
    tournent DÉJÀ en root : su ne demandait aucun mot de passe et le test
    passait quel que soit le mot de passe. La tâche n'était pas vérifiée.
    """
    champ = srv2.check_output("getent shadow root | cut -d: -f2")
    assert champ and not champ.startswith(("!", "*")), message(
        en=f"The root account is locked or has no password: {champ!r}",
        fr=f"Le compte root est verrouillé ou sans mot de passe : {champ!r}",
    )
    verdict = srv2.check_output(
        "getent shadow root | cut -d: -f2 | python3 -c "
        "'import crypt,sys; h=sys.stdin.read().strip(); "
        "print(crypt.crypt(\"SecureP@ss2026!\", h) == h)'"
    )
    assert verdict.strip() == "True", message(
        en="The root password of srv-2 is not SecureP@ss2026! "
        f"(hash {champ[:12]}…).",
        fr="Le mot de passe root de srv-2 n'est pas SecureP@ss2026! "
        f"(hash {champ[:12]}…).",
    )


# ── Section G bis — Logiciel (tâche 16) ────────────────────────────────────

@pytest.mark.points(5)
def test_16_dnf_tree_and_flatpak_calculator(srv1):
    """Tâche 16 : tree installé via DNF + Flatpak Calculator system-wide."""
    # tree installé
    tree = srv1.package("tree")
    assert tree.is_installed, message(
        en="Package tree not installed",
        fr="Paquet tree non installé",
    )
    # Flathub configuré
    remotes = srv1.run("flatpak remotes --system")
    assert "flathub" in remotes.stdout, message(
        en="Remote flathub missing (system)",
        fr="Remote flathub absent (system)",
    )
    # Calculator installé system-wide
    apps = srv1.run("flatpak list --system --app")
    assert "org.gnome.Calculator" in apps.stdout, message(
        en="org.gnome.Calculator not installed system-wide",
        fr="org.gnome.Calculator pas installé system-wide",
    )
