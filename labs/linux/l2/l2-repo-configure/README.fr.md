# Lab — configurer un dépôt dnf

## Rappel

[**dnf sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

Un dépôt se définit par un fichier `.repo` (INI) dans `/etc/yum.repos.d/` :
`[id]`, `name`, `baseurl` (ou `mirrorlist`), `enabled`, `gpgcheck` et `gpgkey`.
Garde `gpgcheck=1` pour que les paquets soient vérifiés par signature.
`dnf repolist` montre les dépôts activés, `dnf repolist --all` tous ceux
configurés.

## Le cours

Les exemples ci-dessous fabriquent puis déclarent un dépôt **local** nommé
`demo-local`, servi depuis `/opt/depot-demo` : le challenge vous demandera un
autre dépôt, sous un autre nom et avec une autre source. Le but est d'apprendre
la méthode, pas de recopier une ligne. Toutes les sorties montrées ont été
produites sur une AlmaLinux 10.2 (`dnf` 4.20.0).

### Ce que dnf connaît déjà, et où c'est écrit

Avant d'ajouter quoi que ce soit, regardez l'existant. `dnf repolist` ne montre
que les dépôts **activés** ; `dnf repolist all` (ou `--all`, les deux formes
fonctionnent) ajoute les désactivés et une colonne `status` :

```bash
dnf repolist
dnf repolist all
```

```text
repo id                repo name                            status
appstream              AlmaLinux 10 - AppStream             enabled
baseos                 AlmaLinux 10 - BaseOS                enabled
crb                    AlmaLinux 10 - CRB                   enabled
extras                 AlmaLinux 10 - Extras                enabled
highavailability       AlmaLinux 10 - HighAvailability      disabled
[...]
```

Un paquet « introuvable » vient neuf fois sur dix d'un dépôt `disabled`, pas
d'un paquet inexistant. Ces dépôts sont décrits dans des fichiers INI de
`/etc/yum.repos.d/` (`almalinux-baseos.repo`, `almalinux-appstream.repo`…). Un
fichier peut contenir **plusieurs sections**, une par dépôt : c'est le nom
entre crochets qui sert d'identifiant à dnf, pas le nom du fichier.

```ini
[appstream]
name=AlmaLinux $releasever - AppStream
mirrorlist=https://mirrors.almalinux.org/mirrorlist/$releasever/appstream
enabled=1
gpgcheck=1
metadata_expire=86400
[...]
```

Deux variables sont substituées par dnf : `$releasever` (la version majeure de
la distribution) et `$basearch` (l'architecture). Une source se déclare soit
par `baseurl` (une URL directe : `https://`, `http://` ou `file://`), soit par
`mirrorlist` (une URL qui renvoie une liste de miroirs à interroger). Les
dépôts livrés par AlmaLinux utilisent la seconde forme.

### Fabriquer un dépôt local

Un dépôt n'est rien d'autre qu'un répertoire de RPM accompagné d'un
sous-répertoire `repodata/` décrivant son contenu. `createrepo_c` produit ce
`repodata/`. Récupérez d'abord un RPM sans l'installer, avec le plugin
`download` :

```bash
sudo dnf install -y createrepo_c
sudo mkdir -p /opt/depot-demo
cd /opt/depot-demo && sudo dnf download bc
sudo createrepo_c /opt/depot-demo
```

```text
Directory walk started
Directory walk done - 1 packages
Pool started (with 5 workers)
Pool finished
```

Le répertoire contient maintenant le RPM et un sous-répertoire `repodata/` :

```bash
ls /opt/depot-demo /opt/depot-demo/repodata
```

```text
/opt/depot-demo:
bc-1.07.1-23.el10.x86_64.rpm  repodata

/opt/depot-demo/repodata:
5099fc6b...-filelists.xml.zst  e63494b7...-other.xml.zst
cd8a8c61...-primary.xml.zst    repomd.xml
```

`repomd.xml` est l'index que dnf lit en premier : il pointe vers les trois
autres fichiers, dont `primary` qui liste les paquets.

> **Pourquoi un dépôt local ?** Vous en contrôlez le contenu et la
> démonstration ne dépend pas du réseau. Un dépôt distant se déclare
> exactement de la même façon, avec une `baseurl` `http(s)://` au lieu de
> `file://` : le guide en donne un exemple.

### Déclarer le dépôt et vérifier que dnf le compte

Créez un fichier dans `/etc/yum.repos.d/`. L'extension `.repo` est obligatoire
(vérifié : renommé en `.conf`, le dépôt disparaît de `repolist`), le reste du
nom est libre :

```ini title="/etc/yum.repos.d/demo-local.repo"
[demo-local]
name=Depot local de demonstration
baseurl=file:///opt/depot-demo
enabled=1
gpgcheck=1
```

Attention à la syntaxe de `file://` : trois barres obliques au total, car
`file://` est le schéma et `/opt/depot-demo` le chemin absolu. `dnf repolist`
liste alors le nouveau dépôt, mais lister ne prouve pas que dnf sache s'en
servir : `-v` affiche le **nombre de paquets** réellement vus, la vraie preuve.

```bash
dnf repolist
dnf repolist -v --repo demo-local
```

```text
Repo-id            : demo-local
Repo-pkgs          : 1
Repo-baseurl       : file:///opt/depot-demo
Repo-filename      : /etc/yum.repos.d/demo-local.repo
```

`Repo-pkgs : 1` : dnf a lu les métadonnées et y trouve un paquet. La nuance a
été vérifiée sur la machine : un dépôt dont la `baseurl` pointe un répertoire
sans `repodata/` **apparaît quand même** dans `dnf repolist`, et c'est
seulement quand dnf tente de lire les métadonnées qu'il échoue.

### Le cache de métadonnées, et pourquoi il ment

dnf ne relit pas les métadonnées à chaque commande, il les met en cache.
Ajoutez un second paquet au dépôt et régénérez son index :

```bash
cd /opt/depot-demo && sudo dnf download dos2unix
sudo createrepo_c --update /opt/depot-demo
dnf repolist -v --repo demo-local | grep Repo-pkgs
```

```text
Repo-pkgs          : 1
```

Toujours 1, alors que le répertoire en contient 2. Il faut invalider le cache
puis le reconstruire :

```bash
dnf clean metadata
dnf repolist -v --repo demo-local | grep Repo-pkgs
```

```text
Cache was expired
29 files removed
Repo-pkgs          : 2
```

> **Le cache de `root` et celui de votre compte sont deux caches différents.**
> Vérifié sur la machine : après `sudo dnf clean metadata`, `sudo dnf repolist`
> annonçait 2 paquets pendant que le `dnf repolist` du compte non privilégié en
> annonçait toujours 1. Le cache de root est dans `/var/cache/dnf`, celui d'un
> utilisateur ordinaire dans `/var/tmp/dnf-<utilisateur>-<aléatoire>`. Nettoyez
> le cache **du compte avec lequel vous constatez le problème**.

`dnf makecache` reconstruit le cache sans attendre la commande suivante ;
`dnf clean all` va plus loin et supprime aussi les RPM téléchargés.

### La signature GPG, le vrai sujet

`gpgcheck=1` impose que chaque RPM soit signé par une clé **présente dans la
base RPM**. Sans cette clé, l'installation s'arrête. Voici le message exact,
obtenu en retirant temporairement la clé AlmaLinux de la base :

```bash
sudo dnf install -y --repo demo-local bc
```

```text
Downloading Packages:
Public key for bc-1.07.1-23.el10.x86_64.rpm is not installed
Error: GPG check FAILED
```

Le paquet a bien été téléchargé : c'est au moment de la vérification que dnf
refuse. `rpm -K` interroge la même chose sur un fichier RPM, sans rien
installer, et c'est l'outil de diagnostic à connaître :

```bash
rpm -K /opt/depot-demo/bc-1.07.1-23.el10.x86_64.rpm
```

```text
bc-1.07.1-23.el10.x86_64.rpm: digests SIGNATURES NOT OK
```

Deux façons d'importer la clé. La première, manuelle, avec `rpm --import` :

```bash
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-10
rpm -qa gpg-pubkey --qf '%{NAME}-%{VERSION}-%{RELEASE} : %{SUMMARY}\n'
```

```text
gpg-pubkey-e37ed158-65785fa9 : Fedora (epel10) <epel@fedora...> key
gpg-pubkey-c2a1e572-668fe8ef : AlmaLinux OS 10 <packager@alma...> key
```

Les clés importées sont stockées dans la base RPM sous forme de faux paquets
nommés `gpg-pubkey-*` : c'est ainsi qu'on inventorie les clés de confiance
d'une machine. Après import, `rpm -K` répond `digests signatures OK` et
l'installation passe.

La seconde façon est de laisser dnf faire le travail, en ajoutant `gpgkey=` au
fichier `.repo`. Cette directive vaut une URL : `https://…` pour la clé
publiée par un éditeur tiers, `file://…` pour une clé déjà sur le disque. Les
clés livrées avec le système sont dans `/etc/pki/rpm-gpg/` :

```ini
gpgkey=<URL ou file:// de la clé publique du dépôt>
```

dnf va alors la chercher, l'affiche et l'importe :

```text
Importing GPG key 0xC2A1E572:
 Userid     : "AlmaLinux OS 10 <packager@almalinux.org>"
 Fingerprint: EE6D B7B9 8F5B F5ED D9DA 0DE5 DEE5 C11C C2A1 E572
 From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-10
Key imported successfully
```

Sans `-y`, dnf affiche l'empreinte puis **demande confirmation** (`Is this ok
[y/N]`) : c'est le moment de la comparer à celle publiée par l'éditeur.
Répondre non donne `Didn't install any keys` puis `Error: GPG check FAILED`.
Dans un script, hors terminal, dnf refuse carrément : `Refusing to
automatically import keys when running unattended. Use "-y" to override.`

Reste la mauvaise solution, celle qui marche. Avec `gpgcheck=0`, l'installation
du même paquet réussit alors que la clé est toujours absente :

```text
Installed:
  bc-1.07.1-23.el10.x86_64
Complete!
```

Rien n'a été vérifié : comme le dit le guide, un dépôt sans `gpgcheck` accepte
n'importe quel RPM modifié en transit. `gpgcheck=0` ne répare rien, il supprime
le contrôle qui vous aurait signalé le problème. Le vrai correctif est
d'importer la bonne clé.

### Activer, désactiver, arbitrer entre dépôts

Éditer le fichier à la main fonctionne, mais `dnf config-manager` fait le même
travail sans risque de faute de frappe. Il **réécrit** le fichier `.repo` :

```bash
sudo dnf config-manager --set-disabled demo-local
dnf repolist all | grep demo-local
sudo dnf config-manager --set-enabled demo-local
```

```text
demo-local             Depot local de demonstration         disabled
```

`--setopt` règle n'importe quelle autre directive. Avec `--save`, la valeur est
écrite dans le fichier ; sans `--save`, elle ne vaut que pour cette commande.
Les deux répondent à des besoins différents : durable contre ponctuel.

```bash
sudo dnf config-manager --setopt=demo-local.priority=10 --save
dnf config-manager --dump demo-local | grep -E '^(priority|enabled) '
```

```text
enabled = 1
priority = 10
```

`priority` arbitre entre deux dépôts qui fournissent **le même paquet** : le
nombre le plus **petit** gagne, la valeur par défaut est 99. Le paquet `bc`
existe à la fois dans `baseos` et dans le dépôt de démonstration, ce qui permet
de le vérifier des deux côtés :

```bash
sudo dnf info bc | grep -E '^(Name|Repository)'      # priority=10
sudo dnf config-manager --setopt=demo-local.priority=100 --save
sudo dnf info bc | grep -E '^(Name|Repository)'      # priority=100
```

```text
Name         : bc
Repository   : demo-local
[...]
Name         : bc
Repository   : baseos
```

Pour un besoin ponctuel, `--disablerepo` et `--enablerepo` ignorent ou activent
un dépôt le temps d'une commande, sans rien modifier sur le disque :

```bash
sudo dnf info bc --disablerepo=demo-local | grep Repository
```

```text
Repository   : baseos
```

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `Warning: failed loading '/etc/.../x.repo', skipping.` puis le dépôt a disparu de `repolist` | erreur de syntaxe INI (ligne avant la première `[section]`, crochet manquant). dnf ignore **tout le fichier** et rend quand même le code 0 |
| Le dépôt s'affiche dans `repolist` mais toute commande échoue sur `Curl error (37)` / `Cannot download repomd.xml` | `baseurl` fausse, source injoignable, ou répertoire sans `repodata/` (lancez `createrepo_c`). Le message nomme le chemin exact tenté : lisez-le |
| `Public key for <paquet>.rpm is not installed` / `Error: GPG check FAILED` | clé absente de la base RPM : `rpm --import`, ou ajoutez `gpgkey=` au `.repo` |
| Un paquet ajouté au dépôt reste invisible | métadonnées en cache : `createrepo_c --update` puis `dnf clean metadata` (avec **le même compte** que celui qui constate le problème) |
| `No such command: config-manager` | plugin absent : `sudo dnf install dnf-plugins-core` (déjà présent sur AlmaLinux 10) |

Pour tout défaire et repartir de zéro :

```bash
sudo dnf remove -y bc
sudo rm -f /etc/yum.repos.d/demo-local.repo
sudo rm -rf /opt/depot-demo
sudo dnf clean all
```

Retirer le fichier `.repo` suffit à faire disparaître le dépôt, mais **pas** à
retirer les paquets déjà installés depuis lui, ni la clé GPG importée. Une clé
se retire comme un paquet, par le nom relevé plus haut :
`sudo rpm -e gpg-pubkey-c2a1e572-668fe8ef`. Ne le faites que pour une clé que
vous avez vous-même ajoutée : retirer celle de la distribution fait échouer
toute installation ultérieure.
