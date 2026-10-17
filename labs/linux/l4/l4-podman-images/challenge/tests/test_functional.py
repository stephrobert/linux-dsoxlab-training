"""Tests pytest+testinfra — l4-podman-images.

La fixture autouse `_apply_lab_state` (conftest.py racine) joue le
`solution.yaml` chiffré du formateur avant les tests (mode CI). En
`dsoxlab check`, elle est désactivée (LAB_NO_REPLAY=1).

On prouve l'ÉTAT : l'image étiquetée dans le magasin, l'archive sur disque, et
sa validité vérifiée par skopeo.
"""
from __future__ import annotations

import pytest

from conftest import lab_host, message

TARGET_HOST = "alma-rhcsa-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(TARGET_HOST)


def test_image_pulled_and_tagged(host):
    """L'image localhost/rapport:v1 doit exister (pull + tag)."""
    res = host.run("podman image exists localhost/rapport:v1")
    assert res.rc == 0, message(
        en="localhost/rapport:v1 must exist: podman pull ubi-micro then "
        "podman tag … localhost/rapport:v1",
        fr="localhost/rapport:v1 doit exister : podman pull ubi-micro puis "
        "podman tag ... localhost/rapport:v1",
    )


def test_image_saved(host):
    """L'archive /root/rapport.tar doit exister et être non vide."""
    archive = host.file("/root/rapport.tar")
    assert archive.exists, message(
        en="/root/rapport.tar must exist: "
        "podman save -o /root/rapport.tar localhost/rapport:v1",
        fr="/root/rapport.tar doit exister : "
        "podman save -o /root/rapport.tar localhost/rapport:v1",
    )
    assert archive.size > 0, message(
        en="/root/rapport.tar must not be empty.",
        fr="/root/rapport.tar ne doit pas être vide.",
    )


def test_archive_is_valid_image(host):
    """skopeo doit inspecter l'archive comme une image valide."""
    res = host.run("skopeo inspect docker-archive:/root/rapport.tar")
    assert res.rc == 0, message(
        en="skopeo inspect docker-archive:/root/rapport.tar must succeed "
        "(a valid image archive produced by podman save).",
        fr="skopeo inspect docker-archive:/root/rapport.tar doit réussir "
        "(archive d'image valide produite par podman save).",
    )
