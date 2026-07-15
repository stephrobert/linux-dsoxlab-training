# Challenge — l1-ssl-certificates

## Mission

À partir de `serveur.crt` (dans `challenge/work/`), produis quatre artefacts de
diagnostic avec `openssl x509`.

## Objectif (fichiers à produire)

1. `sujet.txt` — le **sujet** du certificat.
2. `dates.txt` — les **dates de validité**.
3. `empreinte.txt` — l'**empreinte SHA-256**.
4. `cle-publique.pem` — la **clé publique** extraite.

## Contraintes

- Uniquement `openssl x509 -in serveur.crt -noout <sélecteur>`.
- La validation **relance openssl** sur le certificat et compare : un fichier
  vide ou tapé à la main échoue.

## Validation

```bash
dsoxlab check l1-ssl-certificates
```
