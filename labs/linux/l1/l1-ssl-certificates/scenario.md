# Context — read a TLS certificate

Someone handed you `serveur.crt` and asks the basic questions every admin must
answer from the command line: who is it for, when does it expire, what is its
fingerprint, and what public key does it carry. `openssl x509` reads all of it.

Your mission — in the work directory, produce with `openssl`:

1. `sujet.txt` — the certificate **subject** (its `CN=serveur.lab`).
2. `dates.txt` — the **validity dates** (`notBefore` / `notAfter`).
3. `empreinte.txt` — the **SHA-256 fingerprint**.
4. `cle-publique.pem` — the **public key** extracted from the certificate.

The point: `openssl x509 -in file -noout` plus a selector (`-subject`, `-dates`,
`-fingerprint -sha256`, `-pubkey`) inspects a certificate without a running
server. The tests re-run openssl on the certificate and compare, so a hand-typed
or empty file fails.

Method in the companion guide:
https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/
