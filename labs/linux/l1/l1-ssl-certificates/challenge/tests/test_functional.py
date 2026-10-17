"""test_functional.py — l1-ssl-certificates

Prouve l'ÉTAT des artefacts de diagnostic : chaque attendu est recalculé en
relançant openssl sur le certificat livré, puis comparé au fichier produit par
l'apprenant. Un fichier vide ou copié à la main ne passe pas.

Point de départ : `serveur.crt` (certificat X.509 auto-signé, CN=serveur.lab),
copié par `dsoxlab run`.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

from conftest import message

WORK = pathlib.Path(".")
CRT = WORK / "serveur.crt"


def _openssl(*args: str) -> str:
    res = subprocess.run(
        ["openssl", "x509", "-in", "serveur.crt", "-noout", *args],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert res.returncode == 0, message(
        en=f"openssl failed: {res.stderr}",
        fr=f"openssl a échoué : {res.stderr}",
    )
    return res.stdout


def test_sujet_contains_cn() -> None:
    """sujet.txt contient le CN du certificat (openssl x509 -subject)."""
    f = WORK / "sujet.txt"
    assert f.exists(), message(
        en="sujet.txt is missing. Extract the subject: "
        "openssl x509 -in serveur.crt -noout -subject > sujet.txt",
        fr="sujet.txt manquant. Extrais le sujet : "
        "openssl x509 -in serveur.crt -noout -subject > sujet.txt",
    )
    assert "serveur.lab" in f.read_text(encoding="utf-8"), message(
        en="sujet.txt must contain the CN 'serveur.lab' taken from -subject.",
        fr="sujet.txt doit contenir le CN 'serveur.lab' issu du -subject.",
    )


def test_dates_present() -> None:
    """dates.txt contient les bornes de validité (openssl x509 -dates)."""
    f = WORK / "dates.txt"
    assert f.exists(), message(
        en="dates.txt is missing. Extract the dates: "
        "openssl x509 -in serveur.crt -noout -dates > dates.txt",
        fr="dates.txt manquant. Extrais les dates : "
        "openssl x509 -in serveur.crt -noout -dates > dates.txt",
    )
    content = f.read_text(encoding="utf-8")
    assert "notBefore=" in content and "notAfter=" in content, message(
        en="dates.txt must contain notBefore= and notAfter= (openssl -dates).",
        fr="dates.txt doit contenir notBefore= et notAfter= (openssl -dates).",
    )


def test_empreinte_matches() -> None:
    """empreinte.txt contient l'empreinte SHA-256 réelle du certificat."""
    f = WORK / "empreinte.txt"
    assert f.exists(), message(
        en="empreinte.txt is missing. Compute the fingerprint: "
        "openssl x509 -in serveur.crt -noout -fingerprint -sha256 > empreinte.txt",
        fr="empreinte.txt manquant. Calcule l'empreinte : "
        "openssl x509 -in serveur.crt -noout -fingerprint -sha256 > empreinte.txt",
    )
    expected = _openssl("-fingerprint", "-sha256").split("=", 1)[1].strip()
    got = f.read_text(encoding="utf-8")
    assert expected and expected in got, message(
        en=f"empreinte.txt must contain the certificate's SHA-256 fingerprint "
        f"({expected}). Use -fingerprint -sha256.",
        fr=f"empreinte.txt doit contenir l'empreinte SHA-256 du certificat "
        f"({expected}). Utilise -fingerprint -sha256.",
    )


def test_public_key_extracted() -> None:
    """cle-publique.pem = la clé publique extraite du certificat (PEM)."""
    f = WORK / "cle-publique.pem"
    assert f.exists(), message(
        en="cle-publique.pem is missing. Extract the public key: "
        "openssl x509 -in serveur.crt -noout -pubkey > cle-publique.pem",
        fr="cle-publique.pem manquant. Extrais la clé publique : "
        "openssl x509 -in serveur.crt -noout -pubkey > cle-publique.pem",
    )
    content = f.read_text(encoding="utf-8")
    assert "-----BEGIN PUBLIC KEY-----" in content and (
        "-----END PUBLIC KEY-----" in content
    ), message(
        en="cle-publique.pem must be a PEM public key (openssl -pubkey).",
        fr="cle-publique.pem doit être une clé publique PEM (openssl -pubkey).",
    )
    assert re.search(r"[A-Za-z0-9+/]{40,}", content), message(
        en="cle-publique.pem must contain the key's base64 body.",
        fr="cle-publique.pem doit contenir le corps base64 de la clé.",
    )
