# Lab — inspect a TLS certificate

> Prepare the workspace: `dsoxlab run l1-ssl-certificates`

## Recap

[**TLS diagnostics on the companion guide**](https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/)

`openssl x509 -in cert -noout <selector>` reads a certificate offline: `-subject`
(who), `-issuer` (signed by), `-dates` (validity window), `-fingerprint -sha256`
(a stable identity hash), `-pubkey` (the embedded public key). No server needed.

## Objectives

From `serveur.crt`, produce:

- `sujet.txt` — the subject (`-subject`).
- `dates.txt` — the validity dates (`-dates`).
- `empreinte.txt` — the SHA-256 fingerprint (`-fingerprint -sha256`).
- `cle-publique.pem` — the public key (`-pubkey`).

## Validate

```bash
dsoxlab check l1-ssl-certificates
```
