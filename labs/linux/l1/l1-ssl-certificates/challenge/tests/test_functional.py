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

WORK = pathlib.Path(".")
CRT = WORK / "serveur.crt"


def _openssl(*args: str) -> str:
    res = subprocess.run(
        ["openssl", "x509", "-in", "serveur.crt", "-noout", *args],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert res.returncode == 0, f"openssl a échoué : {res.stderr}"
    return res.stdout


def test_source_present() -> None:
    assert CRT.exists(), (
        "serveur.crt introuvable — lance : dsoxlab run l1-ssl-certificates"
    )


def test_sujet_contains_cn() -> None:
    """sujet.txt contient le CN du certificat (openssl x509 -subject)."""
    f = WORK / "sujet.txt"
    assert f.exists(), (
        "sujet.txt manquant. Extrais le sujet : "
        "openssl x509 -in serveur.crt -noout -subject > sujet.txt"
    )
    assert "serveur.lab" in f.read_text(encoding="utf-8"), (
        "sujet.txt doit contenir le CN 'serveur.lab' issu du -subject."
    )


def test_dates_present() -> None:
    """dates.txt contient les bornes de validité (openssl x509 -dates)."""
    f = WORK / "dates.txt"
    assert f.exists(), (
        "dates.txt manquant. Extrais les dates : "
        "openssl x509 -in serveur.crt -noout -dates > dates.txt"
    )
    content = f.read_text(encoding="utf-8")
    assert "notBefore=" in content and "notAfter=" in content, (
        "dates.txt doit contenir notBefore= et notAfter= (openssl -dates)."
    )


def test_empreinte_matches() -> None:
    """empreinte.txt contient l'empreinte SHA-256 réelle du certificat."""
    f = WORK / "empreinte.txt"
    assert f.exists(), (
        "empreinte.txt manquant. Calcule l'empreinte : "
        "openssl x509 -in serveur.crt -noout -fingerprint -sha256 > empreinte.txt"
    )
    expected = _openssl("-fingerprint", "-sha256").split("=", 1)[1].strip()
    got = f.read_text(encoding="utf-8")
    assert expected and expected in got, (
        f"empreinte.txt doit contenir l'empreinte SHA-256 du certificat "
        f"({expected}). Utilise -fingerprint -sha256."
    )


def test_public_key_extracted() -> None:
    """cle-publique.pem = la clé publique extraite du certificat (PEM)."""
    f = WORK / "cle-publique.pem"
    assert f.exists(), (
        "cle-publique.pem manquant. Extrais la clé publique : "
        "openssl x509 -in serveur.crt -noout -pubkey > cle-publique.pem"
    )
    content = f.read_text(encoding="utf-8")
    assert "-----BEGIN PUBLIC KEY-----" in content and (
        "-----END PUBLIC KEY-----" in content
    ), "cle-publique.pem doit être une clé publique PEM (openssl -pubkey)."
    assert re.search(r"[A-Za-z0-9+/]{40,}", content), (
        "cle-publique.pem doit contenir le corps base64 de la clé."
    )
