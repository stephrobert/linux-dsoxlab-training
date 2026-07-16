"""Tests pytest+testinfra — l4-podman-basic.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : le conteneur web existe, tourne, et utilise la bonne image.
"""
from __future__ import annotations

import pytest

from conftest import lab_host

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_container_running(host):
    """Le conteneur web doit tourner."""
    state = host.check_output(
        "podman inspect -f '{{.State.Running}}' web"
    ).strip()
    assert state == "true", (
        f"Le conteneur web doit tourner (State.Running vu : {state!r}). "
        "podman run -d --name web ... sleep infinity"
    )


def test_container_image(host):
    """Le conteneur doit utiliser l'image ubi9/ubi-micro."""
    image = host.check_output(
        "podman inspect -f '{{.ImageName}}' web"
    ).strip()
    assert "ubi9/ubi-micro" in image, (
        f"Le conteneur web doit utiliser ubi9/ubi-micro (vu : {image!r})."
    )
