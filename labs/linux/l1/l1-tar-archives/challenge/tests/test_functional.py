"""test_functional.py — l1-tar-archives

Prouve l'ÉTAT (les archives réellement produites et leur contenu), pas les
commandes tapées. On ouvre les archives avec le module `tarfile` de Python et on
vérifie leurs membres et la compression réelle — impossible à tromper en tapant
la bonne commande sans produire le bon fichier.

Point de départ : `rapport.txt`, `config.yaml`, `notes.txt`, copiés par
`dsoxlab run`.
"""
from __future__ import annotations

import pathlib
import tarfile

from conftest import message

WORK = pathlib.Path(".")
SOURCES = ("rapport.txt", "config.yaml", "notes.txt")


def _members(archive: str) -> set[str]:
    with tarfile.open(WORK / archive) as tar:
        return {pathlib.PurePath(m.name).name for m in tar.getmembers() if m.isfile()}


def test_targz_created_and_gzip() -> None:
    """docs.tar.gz existe, est un tar RÉELLEMENT gzip, et contient les 3 fichiers."""
    f = WORK / "docs.tar.gz"
    assert f.exists(), message(
        en="docs.tar.gz is missing. Create the gzip archive: "
        "tar czf docs.tar.gz rapport.txt config.yaml notes.txt",
        fr="docs.tar.gz manquant. Crée l'archive gzip : "
        "tar czf docs.tar.gz rapport.txt config.yaml notes.txt",
    )
    assert tarfile.is_tarfile(f), message(
        en="docs.tar.gz is not a valid tar archive.",
        fr="docs.tar.gz n'est pas une archive tar valide.",
    )
    # La compression gzip commence par les octets magiques 1f 8b.
    with open(f, "rb") as fh:
        assert fh.read(2) == b"\x1f\x8b", message(
            en="docs.tar.gz is not gzip-compressed: use the z option (tar czf).",
            fr="docs.tar.gz n'est pas compressé en gzip : utilise l'option z (tar czf).",
        )
    assert _members("docs.tar.gz") == set(SOURCES), message(
        en=f"docs.tar.gz must contain exactly {set(SOURCES)}, "
        f"found {_members('docs.tar.gz')}.",
        fr=f"docs.tar.gz doit contenir exactement {set(SOURCES)}, "
        f"trouvé {_members('docs.tar.gz')}.",
    )


def test_liste_matches_archive() -> None:
    """liste.txt = le listing de l'archive (tar tzf)."""
    f = WORK / "liste.txt"
    assert f.exists(), message(
        en="liste.txt is missing. List the contents: tar tzf docs.tar.gz > liste.txt",
        fr="liste.txt manquant. Liste le contenu : tar tzf docs.tar.gz > liste.txt",
    )
    listed = {
        pathlib.PurePath(ln.strip()).name
        for ln in f.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    }
    assert listed == set(SOURCES), message(
        en=f"liste.txt must list the archive's members {set(SOURCES)}, "
        f"found {listed}.",
        fr=f"liste.txt doit lister les membres de l'archive {set(SOURCES)}, "
        f"trouvé {listed}.",
    )


def test_selective_extract() -> None:
    """extrait/rapport.txt = SEUL rapport.txt extrait, contenu intact (tar xzf ... -C)."""
    extracted = WORK / "extrait" / "rapport.txt"
    assert extracted.exists(), message(
        en="extrait/rapport.txt is missing. Extract a single member into a directory: "
        "mkdir -p extrait && tar xzf docs.tar.gz -C extrait rapport.txt",
        fr="extrait/rapport.txt manquant. Extrais un seul membre dans un dossier : "
        "mkdir -p extrait && tar xzf docs.tar.gz -C extrait rapport.txt",
    )
    assert (
        extracted.read_text(encoding="utf-8")
        == (WORK / "rapport.txt").read_text(encoding="utf-8")
    ), message(
        en="extrait/rapport.txt must be identical to the original rapport.txt.",
        fr="extrait/rapport.txt doit être identique au rapport.txt d'origine.",
    )
    # Extraction SÉLECTIVE : les autres membres ne doivent pas être là.
    for other in ("config.yaml", "notes.txt"):
        assert not (WORK / "extrait" / other).exists(), message(
            en=f"extraction was not selective: {other} was not supposed to be extracted. "
            "Name the member: tar xzf docs.tar.gz -C extrait rapport.txt",
            fr=f"extraction non sélective : {other} ne devait pas être extrait. "
            "Précise le membre : tar xzf docs.tar.gz -C extrait rapport.txt",
        )


def test_bzip2_created() -> None:
    """docs.tar.bz2 existe, est un tar RÉELLEMENT bzip2, et contient les 3 fichiers."""
    f = WORK / "docs.tar.bz2"
    assert f.exists(), message(
        en="docs.tar.bz2 is missing. Create the bzip2 archive: "
        "tar cjf docs.tar.bz2 rapport.txt config.yaml notes.txt",
        fr="docs.tar.bz2 manquant. Crée l'archive bzip2 : "
        "tar cjf docs.tar.bz2 rapport.txt config.yaml notes.txt",
    )
    assert tarfile.is_tarfile(f), message(
        en="docs.tar.bz2 is not a valid tar archive.",
        fr="docs.tar.bz2 n'est pas une archive tar valide.",
    )
    # bzip2 commence par les octets magiques « BZh ».
    with open(f, "rb") as fh:
        assert fh.read(3) == b"BZh", message(
            en="docs.tar.bz2 is not bzip2-compressed: use the j option (tar cjf).",
            fr="docs.tar.bz2 n'est pas compressé en bzip2 : utilise l'option j (tar cjf).",
        )
    assert _members("docs.tar.bz2") == set(SOURCES), message(
        en=f"docs.tar.bz2 must contain exactly {set(SOURCES)}, "
        f"found {_members('docs.tar.bz2')}.",
        fr=f"docs.tar.bz2 doit contenir exactement {set(SOURCES)}, "
        f"trouvé {_members('docs.tar.bz2')}.",
    )
