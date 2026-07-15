# Challenge — l1-ssl-certificates

## Mission

From `serveur.crt` (in `challenge/work/`), produce four diagnostic artifacts with
`openssl x509`.

## Goal (files to produce)

1. `sujet.txt` — the certificate **subject**.
2. `dates.txt` — the **validity dates**.
3. `empreinte.txt` — the **SHA-256 fingerprint**.
4. `cle-publique.pem` — the extracted **public key**.

## Constraints

- Only `openssl x509 -in serveur.crt -noout <sélecteur>`.
- Validation **re-runs openssl** on the certificate and compares: an empty file
  or one typed by hand fails.

## Validation

```bash
dsoxlab check l1-ssl-certificates
```
