# Contexte — lire un certificat TLS

On te remet `serveur.crt` et on te pose les questions de base que tout admin doit
savoir répondre en ligne de commande : pour qui est-il, quand expire-t-il, quelle
est son empreinte, et quelle clé publique porte-t-il. `openssl x509` lit tout ça.

Ta mission — dans le répertoire de travail, produis avec `openssl` :

1. `sujet.txt` — le **sujet** du certificat (son `CN=serveur.lab`).
2. `dates.txt` — les **dates de validité** (`notBefore` / `notAfter`).
3. `empreinte.txt` — l'**empreinte SHA-256**.
4. `cle-publique.pem` — la **clé publique** extraite du certificat.

L'idée : `openssl x509 -in fichier -noout` suivi d'un sélecteur (`-subject`,
`-dates`, `-fingerprint -sha256`, `-pubkey`) inspecte un certificat sans serveur
en marche. Les tests relancent openssl sur le certificat et comparent : un
fichier tapé à la main ou vide échoue.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/
