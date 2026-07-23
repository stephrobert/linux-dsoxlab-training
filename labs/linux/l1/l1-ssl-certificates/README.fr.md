# Lab — inspecter un certificat TLS

## Rappel

[**Diagnostic TLS sur le guide compagnon**](https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/)

`openssl x509 -in cert -noout <sélecteur>` lit un certificat hors ligne :
`-subject` (pour qui), `-issuer` (signé par), `-dates` (fenêtre de validité),
`-fingerprint -sha256` (empreinte d'identité stable), `-pubkey` (la clé publique
embarquée). Aucun serveur requis.

## Le cours

Les exemples ci-dessous fabriquent puis inspectent les certificats d'une API
interne appelée `api.interne.test`, dans le répertoire `~/pki-atelier` : le
challenge, lui, vous remettra un autre certificat, portant un autre nom, et vous
demandera d'autres fichiers de sortie. Le but est d'apprendre à lire et à
vérifier un certificat, pas de recopier une ligne.

Tout se fait **hors ligne**, sans réseau ni autorité publique : c'est la seule
façon d'obtenir un exercice reproductible. Les sorties reproduites ici viennent
d'une AlmaLinux 10 avec **OpenSSL 3.5.5** ; une version plus ancienne peut
présenter le texte autrement. Les empreintes, les numéros de série et les dates
seront évidemment différents chez vous, puisque vos clés le seront : c'est la
**forme** des sorties qu'il faut reconnaître, pas leur contenu.

```bash
mkdir -p ~/pki-atelier && cd ~/pki-atelier
openssl version
# OpenSSL 3.5.5 27 Jan 2026 (Library: OpenSSL 3.5.5 27 Jan 2026)
```

### Trois objets à ne pas confondre

Toute la manipulation découle de ce vocabulaire :

- La **clé privée** est le secret du serveur. Elle ne quitte jamais la machine.
- Le **CSR** (*Certificate Signing Request*) est une **demande** : il contient
  l'identité du serveur et sa **clé publique**, et part chez une autorité.
- Le **certificat** est le CSR **signé**. Il atteste qu'une autorité a validé
  que cette clé publique appartient bien à cette identité.

Un certificat **auto-signé** court-circuite l'autorité : le serveur signe son
propre certificat. Aucun client ne lui fait confiance par défaut. Une **autorité
interne** (CA) résout cela : on lui fait confiance une fois, elle signe ensuite
tous les certificats de la maison.

### Générer une clé privée

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out api.key
```

La commande crache une pluie de points sur la sortie d'erreur pendant la
recherche des nombres premiers : c'est normal, ce n'est pas un message d'erreur.

Un détail que la théorie oublie : le fichier produit est **déjà** en `0600`,
alors que le `umask` de la machine (`0022`) donnerait `0644` à un fichier
ordinaire.

```bash
umask                                 # 0022
touch temoin.txt ; stat -c '%a %n' temoin.txt api.key
```

```text
644 temoin.txt
600 api.key
```

`chmod 600 api.key` reste un bon réflexe (il rattrape une clé recopiée ou
déplacée), mais il ne corrige rien ici : `openssl genpkey` a posé les droits
lui-même. Une clé privée lisible par tous permet d'usurper le service : on ne la
copie pas d'un serveur à l'autre, on ne la versionne jamais.

### Créer une demande de signature, et son `subjectAltName`

Le champ décisif est le **`subjectAltName`** (SAN) : c'est lui qui liste les noms
que le certificat couvre. `-subj` remplit l'identité sans question interactive,
`-addext` ajoute l'extension.

```bash
openssl req -new -key api.key -out api.csr \
  -subj "/C=FR/O=Atelier Interne/CN=api.interne.test" \
  -addext "subjectAltName=DNS:api.interne.test,DNS:api-v2.interne.test"

openssl req -in api.csr -noout -subject
openssl req -in api.csr -noout -text | grep -A1 "Subject Alternative Name"
openssl req -in api.csr -noout -verify
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
                X509v3 Subject Alternative Name:
                    DNS:api.interne.test, DNS:api-v2.interne.test
Certificate request self-signature verify OK
```

Notez l'écriture `C=FR`, sans espace autour du `=`. Beaucoup de documentations
montrent la forme espacée `C = FR` : c'est la même information, mise en forme
autrement, et l'option `-nameopt` fait passer de l'une à l'autre.

```bash
openssl req -in api.csr -noout -subject
openssl req -in api.csr -noout -subject -nameopt oneline
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
subject=C = FR, O = Atelier Interne, CN = api.interne.test
```

Conséquence pratique : un `grep 'CN = api.interne.test'` écrit d'après une
documentation ne trouvera rien sur cette machine. Ne présumez jamais de
l'espacement d'une sortie, regardez-la.

### Le raccourci : le certificat auto-signé

Pour un test local, `-x509` produit directement un certificat, sans CSR ni
autorité :

```bash
openssl req -x509 -key api.key -out api-autosigne.crt -days 365 \
  -subj "/C=FR/O=Atelier Interne/CN=api.interne.test" \
  -addext "subjectAltName=DNS:api.interne.test"
```

Regardez ce qui a été écrit dedans, ce n'est pas ce que vous avez demandé :

```bash
openssl x509 -in api-autosigne.crt -noout -text | sed -n '/X509v3 extensions/,/Signature Algorithm/p'
```

```text
        X509v3 extensions:
            X509v3 Subject Key Identifier:
                58:22:CD:6C:FE:5F:AB:E9:92:17:20:4D:76:6B:D8:12:12:C7:89:29
            X509v3 Authority Key Identifier:
                58:22:CD:6C:FE:5F:AB:E9:92:17:20:4D:76:6B:D8:12:12:C7:89:29
            X509v3 Basic Constraints: critical
                CA:TRUE
            X509v3 Subject Alternative Name:
                DNS:api.interne.test
```

`openssl req -x509` marque le certificat **`CA:TRUE`** par défaut : votre
certificat de service est, techniquement, une autorité de certification. Pour un
certificat feuille, imposez le contraire :

```bash
openssl req -x509 -key api.key -out api-feuille.crt -days 365 \
  -subj "/C=FR/O=Atelier Interne/CN=api.interne.test" \
  -addext "subjectAltName=DNS:api.interne.test" \
  -addext "basicConstraints=critical,CA:FALSE"

openssl x509 -in api-feuille.crt -noout -ext basicConstraints
```

```text
X509v3 Basic Constraints: critical
    CA:FALSE
```

Feuille ou pas, un certificat auto-signé est rejeté à la validation, et c'est
le comportement attendu :

```bash
openssl verify api-feuille.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 18 at 0 depth lookup: self-signed certificate
error api-feuille.crt: verification failed
```

Le code **18** du `Verify return code` que vous croiserez dans un diagnostic TLS
se reproduit donc en local, sans le moindre serveur.

### Monter une autorité maison

Une CA est une clé et un certificat **marqués comme autorité**. La clé est plus
longue, car elle protège toute la chaîne.

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out ca-atelier.key

openssl req -x509 -key ca-atelier.key -out ca-atelier.crt -days 3650 \
  -subj "/C=FR/O=Atelier Interne/CN=Autorite Atelier" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"

openssl x509 -in ca-atelier.crt -noout -ext basicConstraints,keyUsage
```

```text
X509v3 Basic Constraints: critical
    CA:TRUE
X509v3 Key Usage: critical
    Certificate Sign, CRL Sign
```

`CA:TRUE` est ce qui autorise ce certificat à en signer d'autres, `keyCertSign`
ce qui déclare cet usage de la clé.

Attention à la syntaxe : plusieurs extensions se demandent en **une liste
séparée par des virgules**. Répéter l'option ne les cumule pas, elle ne garde
que la dernière, en silence :

```bash
openssl x509 -in ca-atelier.crt -noout -ext basicConstraints -ext keyUsage
```

```text
X509v3 Key Usage: critical
    Certificate Sign, CRL Sign
```

Le `basicConstraints` a disparu de la sortie sans le moindre avertissement.
C'est le genre de détail qui fait conclure à tort qu'une extension est absente.

### Signer, et le piège du `subjectAltName` perdu

L'autorité signe le CSR. Faites d'abord l'erreur, elle est instructive :

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-sans-san.crt -days 365
```

```text
Certificate request self-signature ok
subject=C=FR, O=Atelier Interne, CN=api.interne.test
```

```bash
openssl x509 -in api-sans-san.crt -noout -ext subjectAltName
```

```text
No extensions in certificate
```

Le SAN du CSR a été **perdu**. Deux pièges dans cette seule ligne de sortie :

- le message est trompeur : le certificat **a** des extensions (il a hérité d'un
  `Subject Key Identifier` et d'un `Authority Key Identifier`, visibles avec
  `-text`), simplement pas celle demandée ;
- le code de retour est **`0`**. Un script qui teste `if openssl x509 -ext
  subjectAltName …` conclura que tout va bien. Testez la sortie, pas le code.

La bonne signature réclame **`-copy_extensions copy`**, qui recopie les
extensions du CSR dans le certificat :

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api.crt -days 365 -copy_extensions copy

openssl x509 -in api.crt -noout -subject -issuer
openssl x509 -in api.crt -noout -ext subjectAltName
openssl verify -CAfile ca-atelier.crt api.crt
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
issuer=C=FR, O=Atelier Interne, CN=Autorite Atelier
X509v3 Subject Alternative Name:
    DNS:api.interne.test, DNS:api-v2.interne.test
api.crt: OK
```

`-CAcreateserial` crée au passage un fichier `ca-atelier.srl` qui mémorise le
numéro de série : deux certificats de la même autorité ne doivent jamais
partager le même.

Sans `-CAfile`, la même vérification échoue, faute de savoir à qui faire
confiance :

```bash
openssl verify api.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 20 at 0 depth lookup: unable to get local issuer certificate
error api.crt: verification failed
```

C'est le code **20**, `unable to get local issuer certificate` : l'émetteur est
introuvable. Un client rencontre le même code face à un serveur qui ne sert pas
sa chaîne. Côté serveur, on sert donc la feuille **et** l'autorité concaténées
dans un seul fichier :

```bash
cat api.crt ca-atelier.crt > fullchain.pem
grep -c "BEGIN CERTIFICATE" fullchain.pem      # 2
```

### Lire un certificat : les questions de base

Un certificat se lit toujours de la même façon, avec `-noout` (qui supprime
l'affichage du bloc PEM) suivi d'un sélecteur. Aucun serveur n'est nécessaire :

```bash
openssl x509 -in api.crt -noout -subject -issuer -dates
openssl x509 -in api.crt -noout -fingerprint -sha256
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
issuer=C=FR, O=Atelier Interne, CN=Autorite Atelier
notBefore=Jul 22 14:17:01 2026 GMT
notAfter=Jul 22 14:17:01 2027 GMT
sha256 Fingerprint=4C:48:77:38:83:55:DB:12:11:6D:E3:CB:9E:3A:E4:65:89:3F:81:11:17:6C:AC:D0:49:4F:8A:AD:85:AA:20:D6
```

`subject` et `issuer` diffèrent : ce certificat a bien été signé par un tiers.
Quand les deux sont identiques, c'est un auto-signé. L'**empreinte SHA-256** est
un condensé du certificat entier : elle change au moindre octet modifié, ce qui
en fait un identifiant stable pour comparer deux copies ou consigner ce qui a
été déployé.

Le certificat porte enfin la **clé publique** correspondant à la clé privée. On
peut le prouver en comparant les trois extractions :

```bash
openssl x509 -in api.crt  -noout -pubkey  | openssl sha256
openssl pkey -in api.key  -pubout         | openssl sha256
openssl req  -in api.csr  -noout -pubkey  | openssl sha256
```

```text
SHA2-256(stdin)= 1adee5c51f71a45a806a021d4501efbc57d9e55fb176e8c36ae46fad2180220a
SHA2-256(stdin)= 1adee5c51f71a45a806a021d4501efbc57d9e55fb176e8c36ae46fad2180220a
SHA2-256(stdin)= 1adee5c51f71a45a806a021d4501efbc57d9e55fb176e8c36ae46fad2180220a
```

Les trois condensés sont identiques : la clé, la demande et le certificat
parlent bien du même matériel cryptographique. Celui de l'autorité, lui, est
différent, ce qui est rassurant :

```text
SHA2-256(stdin)= f91e51da80efdac93543a5409a8e5ad7f66008f3f82228bc7e257720282e90c2
```

C'est la vérification à faire quand un service refuse de démarrer en se
plaignant d'une clé qui ne correspond pas à son certificat.

### Les dates, le piège le plus fréquent

Un certificat n'est valide qu'entre `notBefore` et `notAfter`. Fabriquons les
deux pannes classiques. `-not_before` et `-not_after` prennent une date au
format `AAAAMMJJHHMMSSZ`.

Ces deux options sont **récentes** : elles existent sur l'OpenSSL 3.5 de cette
machine, mais pas sur un OpenSSL 3.0 (Debian 12, Ubuntu 22.04), où
`openssl x509 -help` ne les mentionne pas. Sur une telle machine, les
équivalents sont `-startdate` et `-enddate` de la sous-commande `openssl ca`.
Vérifiez d'abord ce dont vous disposez :

```bash
openssl x509 -help 2>&1 | grep -E 'not_before|not_after'
```

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-expire.crt -copy_extensions copy \
  -not_before 20240101000000Z -not_after 20240401000000Z

openssl x509 -in api-expire.crt -noout -dates
openssl verify -CAfile ca-atelier.crt api-expire.crt
```

```text
notBefore=Jan  1 00:00:00 2024 GMT
notAfter=Apr  1 00:00:00 2024 GMT
C=FR, O=Atelier Interne, CN=api.interne.test
error 10 at 0 depth lookup: certificate has expired
error api-expire.crt: verification failed
```

L'autre panne, plus rare et bien plus déroutante, arrive quand l'horloge du
client est en retard ou qu'un certificat a été émis en avance :

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-futur.crt -copy_extensions copy \
  -not_before 20300101000000Z -not_after 20310101000000Z

openssl verify -CAfile ca-atelier.crt api-futur.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 9 at 0 depth lookup: certificate is not yet valid
error api-futur.crt: verification failed
```

Pour la supervision, `-checkend N` répond par un **code de sortie** : `0` si le
certificat est encore valide dans `N` secondes, `1` sinon.

```bash
openssl x509 -in api.crt -noout -checkend 0 ; echo "code $?"
openssl x509 -in api-expire.crt -noout -checkend 0 ; echo "code $?"
```

```text
Certificate will not expire
code 0
Certificate will expire
code 1
```

Sur un certificat émis pour 10 jours, la question « tiendra-t-il 30 jours ? »
se pose ainsi :

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-court.crt -days 10 -copy_extensions copy

openssl x509 -in api-court.crt -noout -dates
openssl x509 -in api-court.crt -noout -checkend 2592000 ; echo "code $?"
```

```text
notBefore=Jul 22 14:18:13 2026 GMT
notAfter=Aug  1 14:18:13 2026 GMT
Certificate will expire
code 1
```

Une limite de `-checkend` mérite d'être connue, car elle passe inaperçue.
Relancez-le sur le certificat qui n'est pas encore valide :

```bash
openssl x509 -in api-futur.crt -noout -checkend 0 ; echo "code $?"
```

```text
Certificate will not expire
code 0
```

Le certificat n'est **pas encore valide**, et `-checkend` répond quand même
`0`. Il ne regarde que `notAfter`. Une supervision qui ne teste que `-checkend`
laissera donc passer un certificat inutilisable : c'est `openssl verify` qui
tranche.

### Ce que `openssl verify` refuse, et ce qu'il laisse passer

Deux cas méritent d'être essayés plutôt que crus sur parole.

**Premier cas : un certificat sans `subjectAltName`.** La règle qu'on lit
partout est qu'il est refusé, le `CN` seul étant ignoré. Reprenons
`api-sans-san.crt`, dont le SAN a été perdu mais dont le `CN` est correct :

```bash
openssl verify -CAfile ca-atelier.crt -verify_hostname api.interne.test api-sans-san.crt
```

```text
api-sans-san.crt: OK
```

Accepté. La chaîne OpenSSL de cette machine (et donc `curl`, qui s'appuie
dessus) retombe sur le `CN` quand aucun SAN de type DNS n'est présent. On peut
le confirmer avec un vrai client, en servant le certificat sur la boucle
locale :

```bash
openssl s_server -accept 8443 -cert api-sans-san.crt -key api.key -www -quiet &
curl -sS -o /dev/null -w 'http=%{http_code}\n' --cacert ca-atelier.crt \
  --resolve api.interne.test:8443:127.0.0.1 https://api.interne.test:8443/
```

```text
http=200
```

Ce que cela veut dire : le guide compagnon rappelle qu'un certificat sans SAN
est refusé, les clients modernes ignorant le `CN`. C'est vrai des navigateurs,
qui embarquent leur propre validateur, mais **pas** des outils en ligne de
commande d'AlmaLinux 10, qui l'acceptent encore. Ne comptez donc pas sur
`openssl verify` ni sur `curl` pour détecter un SAN manquant : lisez-le, avec
`-ext subjectAltName`. Et posez toujours le SAN, car le jour où le service est
appelé depuis un navigateur, il tombe.

Le vrai refus arrive quand le nom demandé **n'est couvert nulle part** :

```bash
openssl verify -CAfile ca-atelier.crt -verify_hostname autre.interne.test api.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 62 at 0 depth lookup: hostname mismatch
error api.crt: verification failed
```

Et côté client, en servant `api.crt` mais en l'appelant sous un autre nom :

```bash
openssl s_server -accept 8443 -cert api.crt -key api.key -www -quiet &
curl -sS -o /dev/null --cacert ca-atelier.crt \
  --resolve autre.interne.test:8443:127.0.0.1 https://autre.interne.test:8443/
```

```text
curl: (60) SSL: no alternative certificate subject name matches target hostname 'autre.interne.test'
```

Retenez surtout que `openssl verify` **ne vérifie pas le nom d'hôte** tant
qu'on ne le lui demande pas : sans `-verify_hostname`, il valide la chaîne et
rien d'autre. Un `OK` ne veut donc pas dire « ce certificat convient à ce
domaine ».

**Second cas : une autorité qui n'en est pas une.** Fabriquons un certificat
marqué `CA:FALSE` et servons-nous-en pour signer :

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out fausse-ca.key
openssl req -x509 -key fausse-ca.key -out fausse-ca.crt -days 365 \
  -subj "/C=FR/O=Atelier Interne/CN=Fausse Autorite" \
  -addext "basicConstraints=critical,CA:FALSE"

openssl x509 -req -in api.csr -CA fausse-ca.crt -CAkey fausse-ca.key \
  -CAcreateserial -out api-fausse.crt -days 365 -copy_extensions copy
```

```text
Certificate request self-signature ok
subject=C=FR, O=Atelier Interne, CN=api.interne.test
```

La signature **réussit** : `openssl x509 -req` ne demande pas à l'émetteur s'il
a le droit de signer, il signe. Le refus n'arrive qu'à la vérification, chez le
client :

```bash
openssl verify -CAfile fausse-ca.crt api-fausse.crt
```

```text
C=FR, O=Atelier Interne, CN=Fausse Autorite
error 79 at 1 depth lookup: invalid CA certificate
error api-fausse.crt: verification failed
```

Deux détails à lire dans ce message : `at 1 depth` désigne le **deuxième**
maillon de la chaîne (l'émetteur, et non la feuille en profondeur `0`), et le
sujet affiché est celui de la fausse autorité. C'est le certificat de l'émetteur
qui est en cause, pas celui du service. Un certificat émis par une autorité mal
formée est donc **inutilisable**, alors même que sa fabrication n'a produit
aucune erreur.

### Faire approuver l'autorité par les clients

Pour que les clients acceptent sans avertissement les certificats de votre
autorité, on installe **`ca-atelier.crt`** (jamais la clé) dans le magasin de
confiance du système :

```bash
# RHEL, AlmaLinux
sudo cp ca-atelier.crt /etc/pki/ca-trust/source/anchors/atelier-interne.crt
sudo update-ca-trust
trust list | grep "Autorite Atelier"

# Debian, Ubuntu (l'extension .crt est obligatoire, sinon le fichier est ignoré)
sudo cp ca-atelier.crt /usr/local/share/ca-certificates/atelier-interne.crt
sudo update-ca-certificates
```

Ces deux commandes modifient un magasin partagé par toute la machine, y compris
par les outils d'administration. Sur une machine de travail collective, il vaut
mieux s'en tenir à `--cacert` (pour `curl`) et `-CAfile` (pour `openssl`), qui
donnent le même résultat pour un test, sans effet de bord et sans privilège.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `error 18 ... self-signed certificate` | certificat auto-signé, aucune autorité derrière |
| `error 20 ... unable to get local issuer certificate` | l'émetteur est introuvable : chaîne incomplète, ou `-CAfile` oublié |
| `error 10 ... certificate has expired` | `notAfter` dépassé, ou horloge du client en avance |
| `error 9 ... certificate is not yet valid` | `notBefore` dans le futur, ou horloge du client en retard |
| `error 62 ... hostname mismatch` | le nom demandé n'est ni dans le SAN ni dans le `CN` |
| `error 79 ... invalid CA certificate` | l'émetteur n'est pas marqué `CA:TRUE` |
| `curl: (60) SSL: no alternative certificate subject name matches...` | même cause que le 62, vue du client |
| `No extensions in certificate` sur `-ext subjectAltName` | l'extension demandée est absente, souvent un `-copy_extensions copy` oublié à la signature |
| Une extension demandée n'apparaît pas dans la sortie | `-ext` répété ne garde que le dernier, écrire `-ext a,b` |
| Le service dit que la clé ne correspond pas au certificat | comparer `openssl x509 -pubkey` et `openssl pkey -pubout`, condensés au `sha256` |
| `openssl verify` dit `OK` mais le navigateur refuse | pas de SAN : `openssl` retombe sur le `CN`, pas le navigateur |
| Un certificat auto-signé se comporte en autorité | `openssl req -x509` pose `CA:TRUE` par défaut, forcer `CA:FALSE` |

### Défaire la démonstration

Tout tient dans un répertoire, il n'y a rien à remettre en état ailleurs :

```bash
pkill -x openssl            # si un openssl s_server tourne encore
rm -rf ~/pki-atelier
```

Si vous avez ajouté l'autorité au magasin de confiance, retirez-la aussi, sinon
la machine continuera de faire confiance à une clé qui traîne :

```bash
sudo rm -f /etc/pki/ca-trust/source/anchors/atelier-interne.crt && sudo update-ca-trust
```
