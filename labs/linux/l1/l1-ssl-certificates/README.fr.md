# Lab — inspecter un certificat TLS

> Prépare l'espace : `dsoxlab run l1-ssl-certificates`

## Rappel

[**Diagnostic TLS sur le guide compagnon**](https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/)

`openssl x509 -in cert -noout <sélecteur>` lit un certificat hors ligne :
`-subject` (pour qui), `-issuer` (signé par), `-dates` (fenêtre de validité),
`-fingerprint -sha256` (empreinte d'identité stable), `-pubkey` (la clé publique
embarquée). Aucun serveur requis.

## Objectifs

À partir de `serveur.crt`, produis :

- `sujet.txt` — le sujet (`-subject`).
- `dates.txt` — les dates de validité (`-dates`).
- `empreinte.txt` — l'empreinte SHA-256 (`-fingerprint -sha256`).
- `cle-publique.pem` — la clé publique (`-pubkey`).

## Valider

```bash
dsoxlab check l1-ssl-certificates
```
