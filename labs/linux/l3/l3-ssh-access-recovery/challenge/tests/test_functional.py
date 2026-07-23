"""Tests pytest+testinfra — l3-ssh-access-recovery.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : la config sshd est VALIDE (sshd -t), sshd tourne, et la
directive de sécurité (PermitRootLogin no) est effective — via sshd -T, pas la
commande tapée.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_sshd_config_valid(host):
    """sshd -t doit réussir : la config n'a plus d'erreur (un reload est sûr)."""
    result = host.run("sshd -t")
    assert result.rc == 0, (
        "sshd -t échoue encore : la config sshd a toujours une directive "
        f"invalide (corrige MaxAuthTries).\n{result.stderr}"
    )


def test_sshd_running(host):
    """Le service sshd doit tourner."""
    assert host.service("sshd").is_running, "sshd doit être actif."


def test_no_invalid_value_left(host):
    """La valeur fautive ne doit plus figurer dans la config."""
    out = host.check_output(
        "cat /etc/ssh/sshd_config.d/99-lab.conf 2>/dev/null || true"
    )
    assert "beaucoup-trop" not in out, (
        "La valeur invalide « beaucoup-trop » est encore présente."
    )


def test_maxauthtries_is_a_number(host):
    """MaxAuthTries doit avoir une valeur numérique valide (effective)."""
    out = host.check_output("sshd -T 2>/dev/null | grep -i '^maxauthtries'")
    parts = out.split()
    assert len(parts) == 2 and parts[1].isdigit(), (
        f"MaxAuthTries doit être un nombre valide et effectif (vu : {out!r})."
    )


def test_permitrootlogin_no_is_effective(host):
    """PermitRootLogin no doit être EFFECTIF, pas seulement écrit quelque part.

    On lit la valeur appliquée avec `sshd -T` : dans sshd_config, c'est la
    PREMIÈRE occurrence rencontrée qui l'emporte, donc une directive présente
    dans le fichier peut très bien ne rien changer. Supprimer le drop-in au
    lieu de le corriger repasse la valeur au défaut (`without-password`, le
    login root par clé est alors autorisé) : c'est ce que ce test refuse.
    """
    result = host.run("sshd -T 2>/dev/null | grep -i '^permitrootlogin'")
    parts = result.stdout.split()
    value = parts[-1].lower() if parts else ""
    assert value == "no", (
        "PermitRootLogin doit être effectif à « no » (vérifié avec sshd -T). "
        f"Vu : {result.stdout.strip()!r}. Si la sortie est vide, c'est que "
        "sshd -T refuse encore la configuration."
    )
