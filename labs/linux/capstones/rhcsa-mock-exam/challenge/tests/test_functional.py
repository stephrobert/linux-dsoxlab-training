"""Tests fonctionnels — capstone rhcsa-mock-exam.

20 tests = 20 tâches du capstone EX200 mock. Chaque test est indépendant
et vérifie l'état observable de la VM cible (pas le chemin pris par
l'apprenant). Pondération via @pytest.mark.points(N) — pour l'instant
décoratif (dsoxlab calcule passed/total), mais sera consommé quand on
ajoutera le plugin pytest-points dans dsoxlab.

Cibles testées :
- alma-rhcsa-1.lab (16 tâches : storage, services, SELinux, NFS export…)
- alma-rhcsa-2.lab (4 tâches : NFS mount, SSH key auth, IP statique, root reset)

Le module conftest.py racine du repo expose ``lab_host(name)`` qui
retourne un host testinfra connecté en SSH+sudo via le ssh_config
OpenSSH généré par dsoxlab (cf. dsoxlab.infra.inventory.write_ssh_config).
"""

from __future__ import annotations

import re

import pytest

from conftest import lab_host, lab_host_ip

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
    assert out.rc == 0, f"parted /dev/vdb échoue : {out.stderr}"
    assert "gpt" in out.stdout.lower(), "Table de partitions GPT attendue sur /dev/vdb"
    # 2 partitions visibles
    parts = re.findall(r"^\s*(\d+)\s+", out.stdout, re.MULTILINE)
    assert len(parts) >= 2, f"Au moins 2 partitions attendues, trouvé : {len(parts)}"


@pytest.mark.points(6)
def test_02_lvm_lvdata_mounted_on_data(srv1):
    """Tâche 2 : VG vgapp + LV lvdata 3 GiB XFS monté sur /data via UUID au boot."""
    # VG existe
    vg = srv1.run("vgs --noheadings -o vg_name vgapp")
    assert vg.rc == 0 and "vgapp" in vg.stdout, "VG vgapp absent"
    # LV existe avec ~3 GiB initial (peut avoir été étendu dans tâche 3)
    lv = srv1.run("lvs --noheadings -o lv_name vgapp/lvdata")
    assert lv.rc == 0 and "lvdata" in lv.stdout, "LV lvdata absent"
    # Monté sur /data en XFS
    mp = srv1.mount_point("/data")
    assert mp.exists, "/data n'est pas un point de montage"
    assert mp.filesystem == "xfs", f"FS attendu xfs, trouvé {mp.filesystem}"
    # Persistant via UUID dans /etc/fstab (pas par chemin /dev/...)
    fstab = srv1.file("/etc/fstab").content_string
    assert re.search(r"^UUID=\S+\s+/data\s+xfs", fstab, re.MULTILINE), (
        "Le mount /data doit être déclaré dans /etc/fstab par UUID en XFS"
    )


@pytest.mark.points(5)
def test_03_lvdata_extended_to_3_5g(srv1):
    """Tâche 3 : lvdata étendu à 3.5 GiB et XFS reflète la nouvelle taille."""
    lv = srv1.run("lvs --noheadings --units g -o lv_size vgapp/lvdata")
    assert lv.rc == 0
    size = float(lv.stdout.strip().rstrip("g").replace(",", "."))
    assert size >= 3.45, f"lvdata doit faire au moins 3.5 GiB, trouvé {size}"
    # XFS résolu : df -h /data doit montrer ~3.5G aussi
    df = srv1.run("df -BG --output=size /data | tail -1")
    df_size = int(df.stdout.strip().rstrip("G"))
    assert df_size >= 3, f"XFS sur /data doit refléter l'extension : {df_size}G"


@pytest.mark.points(4)
def test_04_swapfile_active_persistent(srv1):
    """Tâche 4 : /swapfile 512 MiB activé et persistant via fstab."""
    f = srv1.file("/swapfile")
    assert f.exists, "/swapfile manquant"
    assert f.size >= 500 * 1024 * 1024, f"Taille trop petite : {f.size} bytes"
    # Active
    swap = srv1.run("swapon --show=NAME --noheadings")
    assert "/swapfile" in swap.stdout, "/swapfile pas activé via swapon"
    # Persistant
    fstab = srv1.file("/etc/fstab").content_string
    assert re.search(r"^/swapfile\s+\S+\s+swap", fstab, re.MULTILINE), (
        "/swapfile absent de /etc/fstab"
    )


@pytest.mark.points(6)
def test_05_nfs_export_data_share(srv1):
    """Tâche 5 : /data/share exporté NFS pour srv-2, ports ouverts firewalld."""
    # Service nfs-server actif et activé
    nfs = srv1.service("nfs-server")
    assert nfs.is_running, "nfs-server n'est pas actif"
    assert nfs.is_enabled, "nfs-server pas activé au boot"
    # Export visible
    exp = srv1.run("exportfs -v")
    assert "/data/share" in exp.stdout, "/data/share pas exporté"
    srv2_ip = lab_host_ip(SRV2)
    assert "alma-rhcsa-2" in exp.stdout or srv2_ip in exp.stdout, (
        f"Export non restreint à srv-2 ({srv2_ip} ou son nom) :\n{exp.stdout}"
    )
    # firewalld autorise nfs (et services associés)
    fw = srv1.run("firewall-cmd --list-services --permanent")
    assert "nfs" in fw.stdout, "Service nfs absent de firewalld permanent"


# ── Section B — Utilisateurs, groupes, permissions ──────────────────────────

@pytest.mark.points(5)
def test_06_appuser_uid_password_aging(srv1):
    """Tâche 6 : appuser UID 1500, max 60j, warn 7j."""
    u = srv1.user("appuser")
    assert u.exists, "appuser absent"
    assert u.uid == 1500, f"UID attendu 1500, trouvé {u.uid}"
    assert u.shell == "/bin/bash"
    chage = srv1.run("chage -l appuser")
    assert "Maximum number of days between password change\t: 60" in chage.stdout or \
           re.search(r"Maximum.*:\s*60", chage.stdout), "Max age != 60"
    assert re.search(r"warning.*:\s*7", chage.stdout, re.IGNORECASE), "Warn != 7"


@pytest.mark.points(5)
def test_07_developers_group_and_shared_dir(srv1):
    """Tâche 7 : groupe developers GID 2000 + /srv/shared setgid."""
    g = srv1.group("developers")
    assert g.exists, "groupe developers absent"
    assert g.gid == 2000, f"GID attendu 2000, trouvé {g.gid}"
    assert "appuser" in g.members and "devuser" in g.members, (
        "appuser et devuser doivent être dans developers"
    )
    d = srv1.file("/srv/shared")
    assert d.is_directory, "/srv/shared absent"
    assert d.group == "developers", f"group attendu developers, trouvé {d.group}"
    # Setgid + 775
    mode = int(srv1.run("stat -c %a /srv/shared").stdout.strip(), 8)
    assert mode == 0o2775, f"Mode attendu 2775 (setgid+775), trouvé {oct(mode)}"


@pytest.mark.points(4)
def test_08_acl_appuser_on_myapp_log(srv1):
    """Tâche 8 : ACL user:appuser:rwx sur /var/log/myapp.log."""
    assert srv1.file("/var/log/myapp.log").exists, "/var/log/myapp.log manquant"
    acl = srv1.run("getfacl --absolute-names /var/log/myapp.log")
    assert "user:appuser:rwx" in acl.stdout, (
        f"ACL user:appuser:rwx absente :\n{acl.stdout}"
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
    assert con, "Aucune connexion NetworkManager ne porte la route par défaut."

    methode = host.check_output("nmcli -g ipv4.method con show %s", con)
    assert methode == "manual", (
        "La connexion de gestion est encore en DHCP : elle doit être figée en "
        f"statique (ipv4.method manual). Vu : {methode!r}."
    )

    attendu = lab_host_ip(fqdn)
    adresses = host.check_output("nmcli -g ipv4.addresses con show %s", con)
    assert attendu in adresses, (
        f"La connexion doit déclarer l'adresse {attendu}/24 — celle de la "
        f"machine, à conserver. Vu : {adresses!r}."
    )

    passerelle = host.check_output("nmcli -g ipv4.gateway con show %s", con)
    assert passerelle == "10.10.30.1", (
        f"La passerelle doit être déclarée (10.10.30.1). Vu : {passerelle!r}."
    )

    dns = host.check_output("nmcli -g ipv4.dns con show %s", con)
    assert "10.10.30.1" in dns, (
        "Le DNS du réseau (10.10.30.1) doit être déclaré : c'est lui qui "
        "résout les noms .lab. Déclarer un résolveur public à sa place casse "
        f"le montage NFS par nom de la tâche 18. Vu : {dns!r}."
    )

    # L'adresse doit être RÉELLEMENT portée : un profil modifié mais jamais
    # appliqué ne compte pas.
    live = host.check_output("ip -4 addr show")
    assert attendu in live, (
        f"L'adresse {attendu} n'est pas active : le profil a été modifié mais "
        "pas appliqué (nmcli con up)."
    )


@pytest.mark.points(6)
def test_09_srv1_static_ip_hostname_firewall_8080(srv1):
    """Tâche 9 : srv-1 réseau figé en statique, hostname, port 8080/tcp."""
    _assert_static_pinned(srv1, SRV1)
    hn = srv1.run("hostnamectl --static")
    assert "srv-rhcsa-1.lab" in hn.stdout.strip(), f"Hostname static : {hn.stdout}"
    fw = srv1.run("firewall-cmd --list-ports --permanent")
    assert "8080/tcp" in fw.stdout, "Port 8080/tcp pas ouvert permanent"


@pytest.mark.points(4)
def test_17_srv2_static_ip_hostname(srv2):
    """Tâche 17 : srv-2 réseau figé en statique + hostname srv-rhcsa-2.lab."""
    _assert_static_pinned(srv2, SRV2)
    hn = srv2.run("hostnamectl --static")
    assert "srv-rhcsa-2.lab" in hn.stdout.strip(), f"Hostname static : {hn.stdout}"


# ── Section D — Services ───────────────────────────────────────────────────

@pytest.mark.points(5)
def test_10_myapp_service_running(srv1):
    """Tâche 10 : myapp.service actif, activé au boot, Restart=on-failure."""
    svc = srv1.service("myapp")
    assert svc.is_running, "myapp.service pas actif"
    assert svc.is_enabled, "myapp.service pas activé au boot"
    unit = srv1.file("/etc/systemd/system/myapp.service").content_string
    assert "Restart=on-failure" in unit, "Restart=on-failure manquant"
    assert "ExecStart=/usr/local/bin/myapp.sh" in unit, "ExecStart incorrect"
    assert "User=appuser" in unit, "User=appuser manquant"


@pytest.mark.points(4)
def test_11_weekly_backup_timer(srv1):
    """Tâche 11 : weekly-backup.timer dimanche 03:00, actif et activé."""
    timer = srv1.run("systemctl is-active weekly-backup.timer")
    assert timer.stdout.strip() == "active", "Timer pas actif"
    enabled = srv1.run("systemctl is-enabled weekly-backup.timer")
    assert enabled.stdout.strip() == "enabled", "Timer pas activé au boot"
    show = srv1.run("systemctl cat weekly-backup.timer")
    assert re.search(r"OnCalendar=.*Sun.*03:00", show.stdout), (
        "OnCalendar doit cibler dimanche 03:00"
    )


@pytest.mark.points(4)
def test_12_chrony_server_allows_srv2(srv1):
    """Tâche 12 : chrony source pool.ntp.org + autorise srv-2."""
    chrony = srv1.file("/etc/chrony.conf").content_string
    assert "pool.ntp.org" in chrony or "pool 2.ntp.org" in chrony, (
        "Source pool.ntp.org absente"
    )
    srv2_ip = lab_host_ip(SRV2)
    assert re.search(rf"^allow\s+{re.escape(srv2_ip)}", chrony, re.MULTILINE), (
        f"Directive 'allow {srv2_ip}' absente de /etc/chrony.conf"
    )
    svc = srv1.service("chronyd")
    assert svc.is_running and svc.is_enabled, "chronyd pas actif/activé"


# ── Section E — SELinux ────────────────────────────────────────────────────

@pytest.mark.points(4)
def test_13_restorecon_index_html(srv1):
    """Tâche 13 : /var/www/html/index.html a le contexte httpd_sys_content_t."""
    out = srv1.run("ls -Z /var/www/html/index.html")
    assert "httpd_sys_content_t" in out.stdout, (
        f"Contexte SELinux pas restauré :\n{out.stdout}"
    )


@pytest.mark.points(3)
def test_14_selinux_boolean_httpd_can_network_connect(srv1):
    """Tâche 14 : boolean httpd_can_network_connect=on permanent."""
    out = srv1.run("getsebool httpd_can_network_connect")
    assert "--> on" in out.stdout, f"Boolean pas activé : {out.stdout}"
    # Vérifier persistance : semanage boolean -l doit afficher "on" en colonne default
    perm = srv1.run("semanage boolean -l | grep httpd_can_network_connect")
    # Format : "name (on , on) Description" → 2e champ = persistant
    assert re.search(r"\bon\s*,\s*on\b", perm.stdout), (
        f"Boolean pas persistant : {perm.stdout}"
    )


@pytest.mark.points(3)
def test_15_selinux_port_label_8888_http(srv1):
    """Tâche 15 : port 8888/tcp étiqueté http_port_t."""
    out = srv1.run("semanage port -l")
    found = re.search(r"http_port_t\s+tcp\s+([\d, ]+)", out.stdout)
    assert found, "http_port_t absent de semanage port"
    ports = [p.strip() for p in found.group(1).split(",")]
    assert "8888" in ports, f"Port 8888 pas listé sous http_port_t : {ports}"


# ── Section F — Stockage réseau client ─────────────────────────────────────

@pytest.mark.points(6)
def test_18_srv2_nfs_mount(srv2):
    """Tâche 18 : srv-2 monte alma-rhcsa-1.lab:/data/share sur /mnt/share."""
    mp = srv2.mount_point("/mnt/share")
    assert mp.exists, "/mnt/share n'est pas un point de montage"
    assert mp.filesystem in ("nfs", "nfs4"), f"FS attendu nfs, trouvé {mp.filesystem}"
    fstab = srv2.file("/etc/fstab").content_string
    assert re.search(
        r"alma-rhcsa-1\.lab:/data/share\s+/mnt/share\s+nfs",
        fstab,
    ), "Mount NFS absent de /etc/fstab"
    assert "_netdev" in fstab, "Option _netdev manquante"


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
    assert out.rc == 0, f"SSH key auth échoue : {out.stderr}"
    assert "srv-rhcsa-1" in out.stdout, f"Hostname inattendu : {out.stdout}"
    # PasswordAuthentication désactivé sur srv-2
    sshd = srv2.run("sshd -T 2>/dev/null | grep -i passwordauthentication")
    assert "passwordauthentication no" in sshd.stdout.lower(), (
        f"PasswordAuthentication doit être désactivé : {sshd.stdout}"
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
    assert champ and not champ.startswith(("!", "*")), (
        f"Le compte root est verrouillé ou sans mot de passe : {champ!r}"
    )
    verdict = srv2.check_output(
        "getent shadow root | cut -d: -f2 | python3 -c "
        "'import crypt,sys; h=sys.stdin.read().strip(); "
        "print(crypt.crypt(\"SecureP@ss2026!\", h) == h)'"
    )
    assert verdict.strip() == "True", (
        "Le mot de passe root de srv-2 n'est pas SecureP@ss2026! "
        f"(hash {champ[:12]}…)."
    )


# ── Section G bis — Logiciel (tâche 16) ────────────────────────────────────

@pytest.mark.points(5)
def test_16_dnf_tree_and_flatpak_calculator(srv1):
    """Tâche 16 : tree installé via DNF + Flatpak Calculator system-wide."""
    # tree installé
    tree = srv1.package("tree")
    assert tree.is_installed, "Paquet tree non installé"
    # Flathub configuré
    remotes = srv1.run("flatpak remotes --system")
    assert "flathub" in remotes.stdout, "Remote flathub absent (system)"
    # Calculator installé system-wide
    apps = srv1.run("flatpak list --system --app")
    assert "org.gnome.Calculator" in apps.stdout, (
        "org.gnome.Calculator pas installé system-wide"
    )
