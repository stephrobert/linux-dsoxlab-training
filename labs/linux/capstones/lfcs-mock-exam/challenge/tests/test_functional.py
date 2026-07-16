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

from conftest import lab_host

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
def test_task01_archive_contains_only_logs(host):
    """L'archive doit contenir tous les .log de /srv/audit, et rien d'autre."""
    assert host.file("/root/logs.tar.gz").exists, (
        "/root/logs.tar.gz est absent."
    )
    listing = host.check_output("tar -tzf /root/logs.tar.gz")
    entries = [e for e in listing.split() if e and not e.endswith("/")]
    assert entries, "L'archive est vide."
    bases = {e.rsplit("/", 1)[-1] for e in entries}
    assert {"access.log", "app.log", "kernel.log"} <= bases, (
        "Il manque des .log : les 3 attendus sont access.log, app.log et "
        f"kernel.log (trouvés : {sorted(bases)})."
    )
    intrus = [e for e in entries if not e.endswith(".log")]
    assert not intrus, (
        f"L'archive contient des fichiers qui ne sont pas des .log : {intrus}."
    )


@pytest.mark.points(5)
def test_task02_error_report(host):
    """Le rapport doit contenir exactement les lignes ERROR, dans l'ordre."""
    f = host.file("/root/errors.txt")
    assert f.exists, "/root/errors.txt est absent."
    lignes = [ligne for ligne in f.content_string.splitlines() if ligne.strip()]
    attendu = [
        "ERROR disk almost full",
        "ERROR permission denied",
        "ERROR timeout on backend",
    ]
    assert lignes == attendu, (
        f"Le rapport doit contenir exactement les 3 lignes ERROR dans leur "
        f"ordre d'origine.\nAttendu : {attendu}\nVu : {lignes}"
    )


@pytest.mark.points(4)
def test_task03_links(host):
    """Un lien physique (même inode) et un lien symbolique."""
    src_inode = host.check_output("stat -c %%i %s", "/srv/audit/access.log")
    hard = host.file("/root/access.hard")
    assert hard.exists, "/root/access.hard est absent."
    hard_inode = host.check_output("stat -c %%i %s", "/root/access.hard")
    assert hard_inode == src_inode, (
        "/root/access.hard n'est pas un lien PHYSIQUE vers "
        f"/srv/audit/access.log (inodes différents : {hard_inode} vs "
        f"{src_inode}). Une copie ne compte pas."
    )
    soft = host.file("/root/access.soft")
    assert soft.exists, "/root/access.soft est absent."
    assert soft.is_symlink, "/root/access.soft doit être un lien SYMBOLIQUE."


@pytest.mark.points(6)
def test_task04_collaborative_directory(host):
    """/srv/shared : groupe auditors, mode 2770 (set-GID pour l'héritage)."""
    d = host.file("/srv/shared")
    assert d.exists and d.is_directory, "/srv/shared n'existe pas."
    assert d.group == "auditors", (
        f"Le groupe propriétaire de /srv/shared doit être auditors (vu : "
        f"{d.group})."
    )
    assert d.mode == 0o2770, (
        "Le mode doit être 2770 : le bit set-GID est ce qui fait hériter le "
        f"groupe aux nouveaux fichiers (vu : {oct(d.mode)})."
    )


# ======================================================================
# Section B — Operations Deployment (25 pts)
# ======================================================================


@pytest.mark.points(5)
def test_task05_package_installed_and_held(host):
    """tree doit être installé ET gelé (hold)."""
    assert host.package("tree").is_installed, "Le paquet tree n'est pas installé."
    holds = host.check_output("apt-mark showhold")
    assert "tree" in holds.split(), (
        "tree n'est pas en hold : une mise à jour pourrait le bouger. "
        f"Vu : {holds!r}"
    )


@pytest.mark.points(7)
def test_task06_service_unit(host):
    """labwatch.service doit être activé (boot) et démarré (maintenant)."""
    svc = host.service("labwatch")
    assert svc.is_enabled, (
        "labwatch.service n'est pas enabled : il ne reviendrait pas au reboot."
    )
    assert svc.is_running, "labwatch.service n'est pas démarré."


@pytest.mark.points(7)
def test_task07_timer(host):
    """labreport.timer : activé, actif, déclenchement quotidien à 03:00."""
    timer = host.service("labreport.timer")
    assert timer.is_enabled, "labreport.timer n'est pas enabled."
    assert timer.is_running, "labreport.timer n'est pas actif."
    cal = host.check_output(
        "systemctl show labreport.timer --property=TimersCalendar"
    )
    assert "03:00" in cal, (
        f"Le timer doit se déclencher à 03:00 (OnCalendar). Vu : {cal!r}"
    )
    unit = host.file("/etc/systemd/system/labreport.service")
    assert unit.exists, "L'unité labreport.service est absente."
    assert "labreport.sh" in unit.content_string, (
        "labreport.service doit exécuter /usr/local/bin/labreport.sh."
    )


@pytest.mark.points(6)
def test_task08_cron(host):
    """devops doit avoir une entrée cron toutes les 10 minutes."""
    cron = host.check_output("crontab -u devops -l 2>/dev/null || true")
    assert "labreport.sh" in cron, (
        f"Aucune tâche cron pour devops n'appelle labreport.sh. Vu : {cron!r}"
    )
    ligne = next(
        (ligne for ligne in cron.splitlines()
         if "labreport.sh" in ligne and not ligne.strip().startswith("#")),
        "",
    )
    assert ligne.split()[0] == "*/10", (
        "La tâche doit tourner toutes les 10 minutes (*/10 en champ minute). "
        f"Vu : {ligne!r}"
    )


# ======================================================================
# Section C — Users and Groups (10 pts)
# ======================================================================


@pytest.mark.points(5)
def test_task09_account(host):
    """auditor1 : UID 3001, shell bash, membre du groupe auditors."""
    u = host.user("auditor1")
    assert u.exists, "L'utilisateur auditor1 n'existe pas."
    assert u.uid == 3001, f"L'UID d'auditor1 doit être 3001 (vu : {u.uid})."
    assert u.shell == "/bin/bash", (
        f"Le shell d'auditor1 doit être /bin/bash (vu : {u.shell})."
    )
    assert "auditors" in u.groups, (
        f"auditor1 doit être membre du groupe auditors (vu : {u.groups})."
    )


@pytest.mark.points(5)
def test_task10_sudo_delegation(host):
    """La règle sudo doit être EFFECTIVE pour un membre d'auditors."""
    regles = host.check_output("sudo -l -U auditor1 2>/dev/null || true")
    assert "systemctl status" in regles, (
        "auditor1 (membre d'auditors) n'a pas le droit sudo sur "
        f"systemctl status. Vu :\n{regles}"
    )
    assert "NOPASSWD" in regles, (
        f"La règle doit être NOPASSWD. Vu :\n{regles}"
    )
    assert "(ALL) ALL" not in regles, (
        "La délégation est trop large : auditors ne doit pouvoir lancer QUE "
        f"systemctl status, pas tout. Vu :\n{regles}"
    )


# ======================================================================
# Section D — Networking (25 pts)
# ======================================================================


@pytest.mark.points(8)
def test_task11_static_ip(host):
    """lab0 doit porter 198.51.100.10 en live, et le déclarer dans netplan."""
    addr = host.check_output("ip -4 addr show lab0")
    assert "198.51.100.10" in addr, (
        f"lab0 ne porte pas 198.51.100.10 en live. Vu :\n{addr}"
    )
    conf = host.check_output(
        "grep -rl 198.51.100.10 /etc/netplan/ 2>/dev/null || true"
    )
    assert conf.strip(), (
        "Aucun fichier /etc/netplan/ ne déclare 198.51.100.10 : l'adresse "
        "serait perdue au reboot."
    )


@pytest.mark.points(5)
def test_task12_static_route(host):
    """La route vers 203.0.113.0/24 doit être active."""
    routes = host.check_output("ip route show")
    assert "203.0.113.0/24" in routes, (
        f"La route vers 203.0.113.0/24 est absente. Vu :\n{routes}"
    )


@pytest.mark.points(7)
def test_task13_firewall(host):
    """ufw actif, 8080/tcp autorisé, SSH toujours ouvert."""
    status = host.check_output("ufw status")
    assert "Status: active" in status, (
        f"ufw n'est pas actif. Vu :\n{status}"
    )
    assert "8080/tcp" in status, (
        f"Le port 8080/tcp n'est pas autorisé. Vu :\n{status}"
    )
    assert "OpenSSH" in status or "22/tcp" in status, (
        f"SSH doit rester autorisé. Vu :\n{status}"
    )


@pytest.mark.points(5)
def test_task14_name_resolution(host):
    """lab-target.lab doit résoudre localement vers 198.51.100.10."""
    out = host.check_output("getent hosts lab-target.lab || true")
    assert "198.51.100.10" in out, (
        "Le nom lab-target.lab ne résout pas vers 198.51.100.10 "
        f"(/etc/hosts). Vu : {out!r}"
    )


# ======================================================================
# Section E — Storage (20 pts)
# ======================================================================


@pytest.mark.points(8)
def test_task15_lvm_mount_by_uuid(host):
    """vgdata/lvapp en XFS monté sur /data, persistant PAR UUID."""
    assert host.mount_point("/data").exists, "/data n'est pas monté."
    source, fstype = host.check_output("findmnt -no SOURCE,FSTYPE /data").split()
    assert "vgdata" in source and "lvapp" in source, (
        f"/data doit être monté depuis le LV vgdata/lvapp (vu : {source})."
    )
    assert fstype == "xfs", f"/data doit être en XFS (vu : {fstype})."
    ligne = _fstab_line(host, "/data")
    assert ligne is not None, (
        "Aucune entrée fstab pour /data : le montage serait perdu au reboot."
    )
    assert ligne.split()[0].startswith("UUID="), (
        "L'entrée fstab de /data doit référencer le système de fichiers par "
        f"UUID=, pas par chemin de device. Vu : {ligne!r}"
    )


@pytest.mark.points(7)
def test_task16_quota(host):
    """/srv/quota en XFS avec quotas utilisateur ; devops limité 20M/30M."""
    assert host.mount_point("/srv/quota").exists, "/srv/quota n'est pas monté."
    fstype = host.check_output("findmnt -no FSTYPE /srv/quota")
    assert fstype == "xfs", f"/srv/quota doit être en XFS (vu : {fstype})."
    state = host.check_output('xfs_quota -x -c "state -u" /srv/quota')
    assert "Accounting: ON" in state and "Enforcement: ON" in state, (
        "Les quotas utilisateur ne sont pas appliqués sur /srv/quota "
        f"(option de montage uquota). Vu :\n{state}"
    )
    ligne = _fstab_line(host, "/srv/quota")
    assert ligne is not None, "Aucune entrée fstab pour /srv/quota."
    opts = ligne.split()[3].split(",")
    assert any(o in ("uquota", "usrquota", "quota") for o in opts), (
        "L'entrée fstab doit porter l'option de quota utilisateur, sinon les "
        f"quotas sont perdus au reboot. Vu : {ligne.split()[3]!r}"
    )
    report = host.check_output('xfs_quota -x -c "report -u -N -b" /srv/quota')
    ligne_devops = next(
        (ligne for ligne in report.splitlines()
         if ligne.split() and ligne.split()[0] == "devops"),
        None,
    )
    assert ligne_devops is not None, (
        f"devops n'apparaît pas dans le rapport de quotas. Vu :\n{report}"
    )
    soft, hard = int(ligne_devops.split()[2]), int(ligne_devops.split()[3])
    assert (soft, hard) == (20480, 30720), (
        "devops doit être limité à 20M souple / 30M dur (soit 20480/30720 "
        f"blocs de 1K). Vu : {soft}/{hard}."
    )


@pytest.mark.points(5)
def test_task17_swapfile(host):
    """/swapfile de 256 Mio, actif et persistant."""
    swaps = host.check_output("swapon --show=NAME,SIZE --noheadings || true")
    assert "/swapfile" in swaps, (
        f"/swapfile n'est pas un swap actif. Vu : {swaps!r}"
    )
    taille = host.check_output("stat -c %%s %s", "/swapfile")
    mio = int(taille) // (1024 * 1024)
    assert 250 <= mio <= 262, (
        f"/swapfile doit faire ~256 Mio (vu : {mio} Mio)."
    )
    # Le swap ne se cherche pas comme un montage : la ligne canonique est
    # « /swapfile none swap sw 0 0 » — le 2e champ vaut none, pas swap.
    ligne = next(
        (entree for entree in host.file("/etc/fstab").content_string.splitlines()
         if "/swapfile" in entree and not entree.strip().startswith("#")),
        None,
    )
    assert ligne is not None, (
        "Aucune entrée fstab pour /swapfile : le swap serait perdu au reboot. "
        "Attendu : /swapfile none swap sw 0 0"
    )
    assert "swap" in ligne.split(), (
        f"L'entrée fstab de /swapfile doit être de type swap. Vu : {ligne!r}"
    )
