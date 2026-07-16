"""Tests pytest+testinfra — challenge service-crash-loop.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` officiel du formateur (côté `solution/...`) via
ansible-runner avant les tests — utile pour la CI / validation de
la solution. Quand l'apprenant invoque `dsoxlab check`, la fixture
est désactivée (LAB_NO_REPLAY=1) pour tester son travail manuel
sur la VM.
"""

from __future__ import annotations

import pytest

from conftest import lab_host, lab_target_host

# Lab MULTI-DISTRIB : le diagnostic d'un service en crash-loop est identique
# sur RHEL et Debian (unité systemd + journal), d'où les deux targets du
# lab.yaml. On demande donc l'hôte de la target CHOISIE (dsoxlab check
# --target ubuntu) au lieu d'en coder un en dur — sinon la target Ubuntu
# serait déclarée mais jamais testée.
TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")
SERVICE_NAME = "demo-crashloop"
CONFIG_FILE = "/etc/demo-crashloop/config.yml"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_config_file_exists(host):
    f = host.file(CONFIG_FILE)
    assert f.exists, (
        f"{CONFIG_FILE} doit exister — votre solution a-t-elle créé "
        "/etc/demo-crashloop/config.yml ?"
    )
    assert f.is_file


def test_config_file_permissions(host):
    f = host.file(CONFIG_FILE)
    assert f.user == "root", (
        f"{CONFIG_FILE} doit appartenir à root (vu : {f.user}). "
        "Sur la VM, exécute : sudo chown root:root /etc/demo-crashloop/config.yml"
    )
    assert f.group == "root", (
        f"{CONFIG_FILE} doit appartenir au groupe root (vu : {f.group})."
    )
    assert f.mode == 0o644, (
        f"{CONFIG_FILE} doit avoir le mode 0o644 (vu : {oct(f.mode)}). "
        "Sur la VM, exécute : sudo chmod 0644 /etc/demo-crashloop/config.yml"
    )


def test_config_file_has_port(host):
    content = host.file(CONFIG_FILE).content_string
    assert "port:" in content, (
        f"{CONFIG_FILE} doit contenir une ligne `port: <numero>`. "
        f"Vu : {content[:100]!r}"
    )


def test_service_is_active(host):
    svc = host.service(SERVICE_NAME)
    assert svc.is_running, (
        f"{SERVICE_NAME} doit être actif. Vérifiez `systemctl status "
        f"{SERVICE_NAME}` sur la VM."
    )


def test_service_is_enabled(host):
    """Critère persistence_after_reboot RHCSA — `enabled` au boot."""
    svc = host.service(SERVICE_NAME)
    assert svc.is_enabled, (
        f"{SERVICE_NAME} doit être enabled (persistance reboot). "
        f"Sur la VM, exécute : sudo systemctl enable {SERVICE_NAME} "
        f"(ou bien `systemctl enable --now` qui combine enable + start)."
    )


def test_service_not_crash_looping(host):
    """Le service doit tourner de façon STABLE, pas en boucle de redémarrage.

    On lit l'état réel : un service réparé est en SubState 'running' ; un
    service qui crash-loop est en 'auto-restart' ou 'failed'. (On ne grep pas
    le journal, qui garde l'historique des crashs d'avant le correctif.)
    """
    substate = host.check_output(
        "systemctl show -p SubState --value %s", SERVICE_NAME
    ).strip()
    assert substate == "running", (
        f"{SERVICE_NAME} doit être stable (SubState 'running'), vu : "
        f"{substate!r}. Un service en crash-loop affiche 'auto-restart' ou "
        "'failed' — corrige sa cause (la config manquante) et redémarre-le."
    )
