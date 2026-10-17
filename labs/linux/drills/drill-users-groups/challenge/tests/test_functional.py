"""Tests fonctionnels — drill-users-groups.

5 tests = 5 tâches. On vérifie l'état observable, jamais le chemin pris : peu
importe useradd/usermod/vigr, seul le résultat compte.

Drill BI-DISTRIB : hôte non codé en dur (`lab_target_host()`, dsoxlab >= 0.1.7).
Toutes les assertions ont été sondées sur les DEUX distribs (mêmes chemins
nologin, même champ `passwd -S`, même format `chage -l`).

La délégation sudo est vérifiée en l'EXÉCUTANT réellement, pas en cherchant du
texte dans /etc/sudoers.d : une règle syntaxiquement présente mais inopérante
(mauvais chemin, mauvais groupe) doit échouer.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host, message

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.mark.points(20)
def test_task1_account_to_spec(host):
    """deploy : UID 4200, shell bash, membre supplémentaire d'ops."""
    u = host.user("deploy")
    assert u.exists, message(
        en="User deploy does not exist.",
        fr="L'utilisateur deploy n'existe pas.",
    )
    assert u.uid == 4200, message(
        en=f"deploy's UID must be 4200 (seen: {u.uid}).",
        fr=f"L'UID de deploy doit être 4200 (vu : {u.uid}).",
    )
    assert u.shell == "/bin/bash", message(
        en=f"deploy's shell must be /bin/bash (seen: {u.shell}).",
        fr=f"Le shell de deploy doit être /bin/bash (vu : {u.shell}).",
    )
    assert "ops" in u.groups, message(
        en=f"deploy must be a member of the ops group (seen: {u.groups}).",
        fr=f"deploy doit être membre du groupe ops (vu : {u.groups}).",
    )


@pytest.mark.points(20)
def test_task2_password_aging(host):
    """intern : 30 jours max, 7 jours d'avertissement, compte expirant au 2027-01-01."""
    aging = host.check_output("chage -l intern")
    lignes = {
        ligne.split(":", 1)[0].strip().lower(): ligne.split(":", 1)[1].strip()
        for ligne in aging.splitlines() if ":" in ligne
    }
    maxi = next(
        (v for k, v in lignes.items() if "maximum number" in k), None
    )
    assert maxi == "30", message(
        en=f"intern's password must expire after 30 days at most "
        f"(seen: {maxi!r}).\n{aging}",
        fr=f"Le mot de passe d'intern doit expirer au bout de 30 jours max "
        f"(vu : {maxi!r}).\n{aging}",
    )
    warn = next((v for k, v in lignes.items() if "warning" in k), None)
    assert warn == "7", message(
        en=f"intern must be warned 7 days before expiry (seen: {warn!r}).",
        fr=f"intern doit être averti 7 jours avant expiration (vu : {warn!r}).",
    )
    exp = next((v for k, v in lignes.items() if "account expires" in k), None)
    assert exp and "2027" in exp and "Jan" in exp, message(
        en=f"The intern account must expire on 2027-01-01 (seen: {exp!r}).",
        fr=f"Le compte intern doit expirer le 01/01/2027 (vu : {exp!r}).",
    )


@pytest.mark.points(20)
def test_task3_collaborative_directory(host):
    """/srv/ops : groupe ops, mode 2770 (set-GID = héritage du groupe)."""
    d = host.file("/srv/ops")
    assert d.exists and d.is_directory, message(
        en="/srv/ops does not exist.",
        fr="/srv/ops n'existe pas.",
    )
    assert d.group == "ops", message(
        en=f"The owning group of /srv/ops must be ops (seen: {d.group}).",
        fr=f"Le groupe propriétaire de /srv/ops doit être ops (vu : {d.group}).",
    )
    assert d.mode == 0o2770, message(
        en="The mode must be 2770: the set-GID bit makes created files "
        "inherit the ops group, and \"others\" have no rights at all. "
        f"Seen: {oct(d.mode)}.",
        fr="Le mode doit être 2770 : le bit set-GID fait hériter le groupe ops "
        "aux fichiers créés, et « les autres » n'ont aucun droit. "
        f"Vu : {oct(d.mode)}.",
    )


@pytest.mark.points(20)
def test_task4_sudo_delegation_actually_works(host):
    """Un membre d'ops doit RÉELLEMENT pouvoir lancer le script en root."""
    # On l'exécute vraiment : une règle présente mais inopérante doit échouer.
    res = host.run(
        "runuser -u deploy -- sudo -n /usr/local/bin/ops-report.sh"
    )
    assert res.rc == 0, message(
        en="deploy (a member of ops) cannot run /usr/local/bin/ops-report.sh "
        "as root without a password. The sudo rule is missing, mistargeted or "
        f"requires a password.\nOutput: {res.stdout}{res.stderr}",
        fr="deploy (membre d'ops) ne peut pas lancer /usr/local/bin/ops-report.sh "
        "en root sans mot de passe. La règle sudo est absente, mal ciblée ou "
        f"exige un mot de passe.\nSortie : {res.stdout}{res.stderr}",
    )
    assert "uid=0" in res.stdout, message(
        en=f"The script must run as root (uid=0). Seen: {res.stdout!r}",
        fr=f"Le script doit s'exécuter en root (uid=0). Vu : {res.stdout!r}",
    )

    # « Et rien de plus » : le versant interdit de la tâche. Sans cette
    # assertion, « %ops ALL=(ALL) NOPASSWD: ALL » marquait les 20 points,
    # alors que c'est le root complet, soit l'exact contraire du moindre
    # privilège demandé. Un drill de sécurité doit prouver ce qui est
    # interdit, pas seulement ce qui est permis.
    #
    # Assertion gardée DANS ce test plutôt que dans un test séparé : le score
    # se calcule par test, et les cinq tâches valent 20 points chacune. Un
    # sixième test ramènerait chaque tâche à 16,7 points.
    #
    # /usr/bin/id sert de témoin : aucune raison de le déléguer, et son refus
    # est net (sudo sort en erreur avec « not allowed to execute »).
    trop_large = host.run("runuser -u deploy -- sudo -n /usr/bin/id")
    assert trop_large.rc != 0, message(
        en="deploy can run /usr/bin/id as root, although the task only "
        "delegates /usr/local/bin/ops-report.sh. The sudo rule is too "
        "broad (a NOPASSWD: ALL, or a path set to ALL): it grants full "
        "root. Narrow it down to the single command asked for.\n"
        f"Output: {trop_large.stdout}{trop_large.stderr}",
        fr="deploy peut lancer /usr/bin/id en root, alors que la tâche ne "
        "délègue que /usr/local/bin/ops-report.sh. La règle sudo est trop "
        "large (un NOPASSWD: ALL, ou un chemin en ALL) : elle accorde le root "
        "complet. Restreins-la à la seule commande demandée.\n"
        f"Sortie : {trop_large.stdout}{trop_large.stderr}",
    )


@pytest.mark.points(20)
def test_task5_departing_account_locked(host):
    """former : mot de passe verrouillé ET shell qui interdit la connexion."""
    statut = host.check_output("passwd -S former")
    champ = statut.split()[1] if len(statut.split()) > 1 else "?"
    assert champ == "L", message(
        en="former's password must be LOCKED (passwd -S must "
        f"show L in the 2nd field). Seen: {statut!r}",
        fr="Le mot de passe de former doit être VERROUILLÉ (passwd -S doit "
        f"afficher L en 2e champ). Vu : {statut!r}",
    )
    shell = host.user("former").shell
    # L'énoncé demande un shell qui « interdit la connexion », pas nommément
    # nologin : /bin/false et /sbin/nologin remplissent tous deux le contrat.
    # N'accepter que nologin recalait une réponse juste.
    assert shell.endswith(("nologin", "false")), message(
        en="former's shell must forbid logging in (…/nologin or "
        "/bin/false): locking the password is not enough, an SSH key "
        f"would still get through. Seen: {shell}.",
        fr="Le shell de former doit interdire la connexion (…/nologin ou "
        "/bin/false) : verrouiller le mot de passe ne suffit pas, une clé SSH "
        f"passerait encore. Vu : {shell}.",
    )
