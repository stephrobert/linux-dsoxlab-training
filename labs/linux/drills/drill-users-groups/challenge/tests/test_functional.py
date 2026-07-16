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

from conftest import lab_host, lab_target_host

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.mark.points(20)
def test_task1_account_to_spec(host):
    """deploy : UID 4200, shell bash, membre supplémentaire d'ops."""
    u = host.user("deploy")
    assert u.exists, "L'utilisateur deploy n'existe pas."
    assert u.uid == 4200, f"L'UID de deploy doit être 4200 (vu : {u.uid})."
    assert u.shell == "/bin/bash", (
        f"Le shell de deploy doit être /bin/bash (vu : {u.shell})."
    )
    assert "ops" in u.groups, (
        f"deploy doit être membre du groupe ops (vu : {u.groups})."
    )


@pytest.mark.points(20)
def test_task2_password_aging(host):
    """intern : 30 jours max, 7 jours d'avertissement, compte expirant fin 2026."""
    aging = host.check_output("chage -l intern")
    lignes = {
        ligne.split(":", 1)[0].strip().lower(): ligne.split(":", 1)[1].strip()
        for ligne in aging.splitlines() if ":" in ligne
    }
    maxi = next(
        (v for k, v in lignes.items() if "maximum number" in k), None
    )
    assert maxi == "30", (
        f"Le mot de passe d'intern doit expirer au bout de 30 jours max "
        f"(vu : {maxi!r}).\n{aging}"
    )
    warn = next((v for k, v in lignes.items() if "warning" in k), None)
    assert warn == "7", (
        f"intern doit être averti 7 jours avant expiration (vu : {warn!r})."
    )
    exp = next((v for k, v in lignes.items() if "account expires" in k), None)
    assert exp and "2027" in exp and "Jan" in exp, (
        f"Le compte intern doit expirer le 01/01/2027 (vu : {exp!r})."
    )


@pytest.mark.points(20)
def test_task3_collaborative_directory(host):
    """/srv/ops : groupe ops, mode 2770 (set-GID = héritage du groupe)."""
    d = host.file("/srv/ops")
    assert d.exists and d.is_directory, "/srv/ops n'existe pas."
    assert d.group == "ops", (
        f"Le groupe propriétaire de /srv/ops doit être ops (vu : {d.group})."
    )
    assert d.mode == 0o2770, (
        "Le mode doit être 2770 : le bit set-GID fait hériter le groupe ops "
        "aux fichiers créés, et « les autres » n'ont aucun droit. "
        f"Vu : {oct(d.mode)}."
    )


@pytest.mark.points(20)
def test_task4_sudo_delegation_actually_works(host):
    """Un membre d'ops doit RÉELLEMENT pouvoir lancer le script en root."""
    # On l'exécute vraiment : une règle présente mais inopérante doit échouer.
    res = host.run(
        "runuser -u deploy -- sudo -n /usr/local/bin/ops-report.sh"
    )
    assert res.rc == 0, (
        "deploy (membre d'ops) ne peut pas lancer /usr/local/bin/ops-report.sh "
        "en root sans mot de passe. La règle sudo est absente, mal ciblée ou "
        f"exige un mot de passe.\nSortie : {res.stdout}{res.stderr}"
    )
    assert "uid=0" in res.stdout, (
        f"Le script doit s'exécuter en root (uid=0). Vu : {res.stdout!r}"
    )


@pytest.mark.points(20)
def test_task5_departing_account_locked(host):
    """former : mot de passe verrouillé ET shell qui interdit la connexion."""
    statut = host.check_output("passwd -S former")
    champ = statut.split()[1] if len(statut.split()) > 1 else "?"
    assert champ == "L", (
        "Le mot de passe de former doit être VERROUILLÉ (passwd -S doit "
        f"afficher L en 2e champ). Vu : {statut!r}"
    )
    shell = host.user("former").shell
    assert shell.endswith("nologin"), (
        "Le shell de former doit interdire la connexion (…/nologin) : "
        "verrouiller le mot de passe ne suffit pas, une clé SSH passerait "
        f"encore. Vu : {shell}."
    )
