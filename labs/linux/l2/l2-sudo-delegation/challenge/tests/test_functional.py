"""Tests pytest+testinfra — l2-sudo-delegation.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le drop-in existe, sa syntaxe est valide (visudo -c), et la
politique sudo effective d'ops autorise systemctl sans mot de passe — lu via
`sudo -l -U ops`, pas la commande tapée.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"
DROPIN = "/etc/sudoers.d/operators"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_dropin_exists(host):
    """Le drop-in sudoers pour operators doit exister."""
    assert host.file(DROPIN).exists, (
        f"{DROPIN} manquant. Crée la délégation dans /etc/sudoers.d/."
    )


def test_sudoers_syntax_valid(host):
    """L'ensemble sudoers (drop-in inclus) doit être syntaxiquement valide."""
    rc = host.run("visudo -c").rc
    assert rc == 0, (
        "visudo -c échoue. Deux causes possibles : une syntaxe invalide (un "
        "drop-in cassé peut bloquer TOUT sudo), ou de mauvais droits sur le "
        "drop-in. visudo -f laisse le fichier en 0640 et visudo -c exige 0440 : "
        "vérifie ls -l /etc/sudoers.d/ avant de chercher une faute de frappe."
    )


def test_ops_can_run_systemctl_nopasswd(host):
    """La politique effective d'ops doit autoriser systemctl sans mot de passe."""
    out = host.check_output("sudo -l -U ops")
    assert "/usr/bin/systemctl" in out, (
        "ops doit pouvoir lancer /usr/bin/systemctl via sudo "
        f"(sudo -l -U ops ne le montre pas).\n{out}"
    )
    assert "NOPASSWD" in out, (
        "systemctl doit être autorisé SANS mot de passe (NOPASSWD) pour ops."
    )


def test_delegation_is_limited(host):
    """Moindre privilège : ops ne doit PAS avoir un sudo total (ALL)."""
    out = host.check_output("sudo -l -U ops")
    # Une ligne « (ALL) ALL » ou « (ALL : ALL) ALL » donnerait tout : à proscrire.
    for line in out.splitlines():
        stripped = line.strip()
        if stripped.endswith(") ALL") and "systemctl" not in stripped:
            pytest.fail(
                "ops a un sudo trop large (tout est permis). Restreins la "
                f"délégation à /usr/bin/systemctl.\nLigne : {stripped!r}"
            )
