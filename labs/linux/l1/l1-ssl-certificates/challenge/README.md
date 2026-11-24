# Read a TLS certificate

## The situation

Someone handed you `serveur.crt` and asks the basic questions every admin must
answer from the command line: who is it for, when does it expire, what is its
fingerprint, and what public key does it carry.

The point: `openssl` reads all of it offline, from the file, with no server
running. Each question has its own selector, which you have to go and find. The
tests re-run openssl on the certificate and compare, so a hand-typed or empty
file fails.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/networks/fundamentals/tls-diagnostics/

## What is asked

### Mission

From `serveur.crt` (in `challenge/work/`), produce four diagnostic artifacts with
`openssl x509`.

### Goal (files to produce)

1. `sujet.txt` — the certificate **subject**.
2. `dates.txt` — the **validity dates**.
3. `empreinte.txt` — the **SHA-256 fingerprint**.
4. `cle-publique.pem` — the extracted **public key**.

### Constraints

- Only `openssl x509 -in serveur.crt -noout <sélecteur>`.
- Validation **re-runs openssl** on the certificate and compares: an empty file
  or one typed by hand fails.

### Validation

```bash
dsoxlab check l1-ssl-certificates
```
