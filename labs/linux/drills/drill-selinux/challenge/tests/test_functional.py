"""Tests fonctionnels — drill-selinux.

4 tests = 4 tâches. Drill MONO-DISTRIB (RHCSA) : SELinux n'a pas d'équivalent
Debian, LFCS a drill-apparmor.

Les contextes sont vérifiés APRÈS une relabellisation (fixture ci-dessous) :
un `chcon` posé à la main ne survit pas à un `restorecon`, seul un
`semanage fcontext` le fait. Le piège est intégré aux tâches, pas annoncé.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host, message

TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


@pytest.fixture(scope="module", autouse=True)
def _relabel(host):
    """Relabellise avant les tests : ce qui n'est pas dans la policy meurt ici."""
    host.run("restorecon -R /srv/web")


@pytest.mark.points(25)
def test_task1_enforcing_and_persistent(host):
    """SELinux doit être en enforcing MAINTENANT et après un reboot."""
    mode = host.check_output("getenforce")
    assert mode == "Enforcing", message(
        en=f"SELinux must be Enforcing (seen: {mode!r}).",
        fr=f"SELinux doit être en Enforcing (vu : {mode!r}).",
    )
    conf = host.file("/etc/selinux/config").content_string
    ligne = next(
        (entree.strip() for entree in conf.splitlines()
         if entree.strip().startswith("SELINUX=")),
        "",
    )
    assert ligne == "SELINUX=enforcing", message(
        en="setenforce 1 does not survive a reboot: /etc/selinux/config must "
        f"declare SELINUX=enforcing. Seen: {ligne!r}",
        fr="setenforce 1 ne survit pas au reboot : /etc/selinux/config doit "
        f"déclarer SELINUX=enforcing. Vu : {ligne!r}",
    )


@pytest.mark.points(25)
def test_task2_context_survives_relabel(host):
    """Le contexte de /srv/web doit survivre à une relabellisation."""
    ctx = host.check_output("ls -Zd /srv/web/index.html").split()[0]
    assert "httpd_sys_content_t" in ctx, message(
        en="The context of /srv/web/index.html is not httpd_sys_content_t "
        "AFTER a relabelling: a chcon was set by hand, and it did not "
        "survive. Only a rule in the policy holds. "
        f"Seen: {ctx}",
        fr="Le contexte de /srv/web/index.html n'est pas httpd_sys_content_t "
        "APRÈS une relabellisation : un chcon a été posé à la main, il n'a pas "
        "survécu. Seule une règle dans la policy tient. "
        f"Vu : {ctx}",
    )


@pytest.mark.points(25)
def test_task3_boolean_persistent(host):
    """Le booléen doit être actif ET persistant."""
    etat = host.check_output("getsebool httpd_can_network_connect")
    assert "--> on" in etat, message(
        en=f"The httpd_can_network_connect boolean must be on. Seen: {etat!r}",
        fr=f"Le booléen httpd_can_network_connect doit être on. Vu : {etat!r}",
    )
    # -P écrit la valeur dans la policy : sans lui, elle est perdue au reboot.
    persiste = host.check_output(
        "semanage boolean -l -C 2>/dev/null | grep httpd_can_network_connect || true"
    )
    assert "on" in persiste, message(
        en="The boolean is on but NOT persistent: it must be written into the "
        "policy (the -P option), otherwise it falls back at reboot. "
        f"Seen: {persiste!r}",
        fr="Le booléen est actif mais PAS persistant : il faut l'écrire dans la "
        "policy (option -P), sinon il retombe au reboot. "
        f"Vu : {persiste!r}",
    )


@pytest.mark.points(25)
def test_task4_port_labelled(host):
    """Le port 8888/tcp doit porter le label http_port_t."""
    ports = host.check_output(
        "semanage port -l 2>/dev/null | grep '^http_port_t' || true"
    )
    assert "8888" in ports, message(
        en="Port 8888/tcp does not carry the http_port_t label: a web service "
        "could not bind to it, SELinux would refuse. "
        f"Seen: {ports!r}",
        fr="Le port 8888/tcp ne porte pas le label http_port_t : un service web "
        "ne pourrait pas s'y attacher, SELinux le refuserait. "
        f"Vu : {ports!r}",
    )
