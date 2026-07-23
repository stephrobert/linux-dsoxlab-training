# Lab — authentification LDAP avec SSSD

## Rappel

[**SSSD + LDAP sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/)

SSSD est le démon client qui interroge un annuaire LDAP pour le compte du
système. Sa configuration vit dans `/etc/sssd/sssd.conf` (mode `0600`
obligatoire) et déclare un domaine avec `id_provider`, `ldap_uri` et
`ldap_search_base`. `authselect` branche ensuite NSS et PAM sur SSSD, après quoi
`getent passwd` et `id` répondent depuis l'annuaire.

## Le cours

Tous les exemples ci-dessous portent sur un **autre annuaire et d'autres
comptes** que le challenge : une machine d'atelier AlmaLinux 10 qui héberge à la
fois un 389 Directory Server de base `dc=atelier,dc=demo` et le client SSSD. On y
trouve l'utilisateur `nlefevre` (uid `4201`) et le groupe `redaction`
(gid `4200`). Toutes les sorties de ce cours ont été produites sur cette machine.

### La chaîne d'identité : NSS répond « qui », PAM répond « avec quel mot de passe »

Quand vous tapez `id`, le système ne sait pas d'emblée où chercher : c'est
`/etc/nsswitch.conf` qui lui dit dans quel ordre consulter les sources. Quand
vous vous connectez, c'est PAM qui décide comment vérifier le mot de passe. Les
deux chaînes sont **indépendantes**, et SSSD sert les deux :

```text
getent / id        login / su / ssh
     |                    |
  nsswitch             PAM (pam_sss)
     |                    |
     +-------- SSSD ------+   (cache local sur disque)
               |
            LDAP (annuaire)
```

Cette indépendance explique la moitié des pannes du sujet : un compte peut être
parfaitement visible par `getent passwd` et refuser toute connexion, et
l'inverse est vrai aussi. `getent` sait d'ailleurs interroger **une seule
source** avec `-s`, ce qui tranche immédiatement la question « d'où vient ce
compte ? » :

```bash
getent -s files passwd nlefevre   # rien, rc=2 : aucun compte local
getent -s sss   passwd nlefevre   # nlefevre:*:4201:4200:...:/bin/bash
getent -s files passwd student    # student:x:1000:1000::/home/student:/bin/bash
```

Le compte d'annuaire n'existe que dans `sss`, le compte local que dans `files`.
C'est exactement ce que prouvera votre validation.

### Installer les paquets et écrire `sssd.conf`

Sur AlmaLinux 10, le démon et le connecteur LDAP sont dans deux paquets
distincts, auxquels s'ajoutent le module de création du home et l'outillage
d'inspection :

```bash
sudo dnf install -y sssd-ldap oddjob-mkhomedir sssd-tools openldap-clients
```

Deux remarques qui font gagner du temps : `sssd-common` (donc le démon et
`sss_cache`) est déjà présent sur une installation minimale, mais **`sssctl`
n'est pas installé par défaut** : il vient de `sssd-tools`. Quant à
`openldap-servers`, il n'existe plus sur RHEL 10 et dérivées ; côté serveur, on
utilise `389-ds-base`.

Toute la configuration client tient dans un fichier :

```ini
[sssd]
services = nss, pam
domains = ATELIER

[domain/ATELIER]
id_provider = ldap
auth_provider = ldap
ldap_uri = ldap://10.10.30.14
ldap_search_base = dc=atelier,dc=demo
ldap_id_use_start_tls = False
override_homedir = /home/%u
default_shell = /bin/bash
cache_credentials = true
```

Ce qui compte : `id_provider` et `auth_provider` désignent la source
(identité et authentification) ; `ldap_uri` l'adresse du serveur ;
`ldap_search_base` la branche où chercher les comptes ; `override_homedir` et
`default_shell` imposent un home et un shell même si l'annuaire ne les fournit
pas ; `cache_credentials = true` autorise la connexion annuaire injoignable.
Le nom du domaine (`ATELIER` ici) est libre, mais il doit être repris à
l'identique dans `domains =` et dans `[domain/...]`.

> Le guide montre `config_file_version = 2` en tête de `[sssd]`. Sur SSSD 2.12
> (AlmaLinux 10), la directive est encore tolérée mais `sssctl config-check` la
> signale comme non autorisée ; elle n'est plus nécessaire.

**Le fichier doit être en `0600`, sinon SSSD refuse de démarrer.** Ce n'est pas
une recommandation, c'est un contrôle au démarrage. Avec un `0644` :

```bash
sudo systemctl start sssd
sudo journalctl -u sssd -n 5 --no-pager
```

```text
sssd[29861]: [sssd] [access_check_file] (0x0020): Unexpected access to '/etc/sssd/sssd.conf' by other users
sssd[29861]: Can't read config: 'File ownership and permissions check failed'
sssd[29861]: Make sure configuration is readable by the user used to run service and doesn't have public rwx bits set.
```

Un `sudo chmod 0600 /etc/sssd/sssd.conf` suivi d'un `systemctl start sssd` règle
l'affaire. Notez que l'unité systemd repose elle-même les droits attendus :
après démarrage, le fichier appartient à `root:sssd` en `-rw-r-----`.

### Brancher NSS et PAM avec `authselect`

`authconfig` a disparu de RHEL 8 et suivantes : c'est `authselect` qui écrit
désormais `/etc/nsswitch.conf` et les fichiers de `/etc/pam.d/`. On commence
toujours par regarder d'où l'on part :

```bash
sudo authselect current
sudo authselect list
```

```text
Profile ID: local
Enabled features: None

- local  	 Local users only
- sssd   	 Enable SSSD for system authentication (also for local users only)
- winbind	 Enable winbind for system authentication
```

Chaque profil expose des **fonctionnalités** optionnelles, à lister avant de
choisir (`authselect list-features sssd` en donne plus de vingt, dont
`with-mkhomedir`, `with-sudo`, `with-faillock`). La bascule :

```bash
sudo authselect select sssd with-mkhomedir
```

Il faut voir ce que la commande écrit réellement. Avant, `/etc/nsswitch.conf` ne
connaissait que les fichiers locaux ; après, la source `sss` est insérée :

```text
# avant (profil local)
passwd:  files systemd
group:   files [SUCCESS=merge] systemd
shadow:  files systemd

# après (profil sssd)
passwd:  files sss systemd
group:   files [SUCCESS=merge] sss [SUCCESS=merge] systemd
shadow:  files systemd
```

`files` reste **en premier** : un compte local continue d'être résolu
localement, l'annuaire n'est consulté que pour ce qu'il ne trouve pas. À noter,
contrairement à ce que suggère le guide : sur AlmaLinux 10, le profil `sssd`
n'ajoute `sss` qu'à `passwd` et `group`, **pas à `shadow`**.

Côté PAM, `/etc/pam.d/system-auth` gagne trois lignes (les deux `pam_usertype` et
`pam_localuser` servent à sauter `pam_unix` pour un compte non local) :

```text
auth     [default=1 ignore=ignore success=ok]  pam_localuser.so
auth     sufficient   pam_unix.so nullok
auth     sufficient   pam_sss.so forward_pass
session  optional     pam_oddjob_mkhomedir.so
session  optional     pam_sss.so
```

Ces fichiers sont des liens symboliques vers `/etc/authselect/`, et
`authselect check` vérifie cette cohérence :

```bash
sudo authselect check
```

```text
Current configuration is valid.
```

Si l'un des fichiers a été remplacé par une copie éditée à la main, le contrôle
échoue clairement (code de retour 3) :

```text
[error] [/etc/pam.d/system-auth] is not a symbolic link!
[error] [/etc/pam.d/system-auth] was not created by authselect!
Current configuration is not valid. It was probably modified outside authselect.
```

> Sur authselect 1.5.2 (AlmaLinux 10), un `authselect select` **sans `--force`**
> ne s'arrête pas dans ce cas : il affiche les mêmes erreurs, ajoute « These
> changes will be overwritten. Please call 'authselect opt-out' in order to keep
> them », puis écrase quand même. Ne comptez donc pas sur l'absence de `--force`
> comme garde-fou : faites une copie de `/etc/pam.d/` avant de manipuler.

Il reste à démarrer le démon, et **`oddjobd`** si vous avez demandé
`with-mkhomedir` : `authselect` le rappelle lui-même dans sa sortie.

```bash
sudo systemctl enable --now sssd oddjobd
```

### Vérifier : résolution, puis connexion réelle

Le premier test ne touche pas au mot de passe, il vérifie seulement que le
système **voit** le compte :

```bash
getent passwd nlefevre
id nlefevre
getent group redaction
```

```text
nlefevre:*:4201:4200:Nadia Lefevre:/home/nlefevre:/bin/bash
uid=4201(nlefevre) gid=4200(redaction) groups=4200(redaction)
redaction:*:4200:
```

Le second exerce toute la chaîne PAM. Un simple `su -` depuis un compte non
privilégié suffit, sans toucher à la configuration SSH :

```bash
su - nlefevre -c id
```

```text
Password:
uid=4201(nlefevre) gid=4200(redaction) groups=4200(redaction) ...
```

Lors du tout premier essai, `oddjobd` étant à l'arrêt, la connexion réussit mais
le home manque : `su: warning: cannot change directory to /home/nlefevre: No
such file or directory`. Après `systemctl enable --now oddjobd`,
`pam_oddjob_mkhomedir` fait son travail et `ls -ld /home/nlefevre` renvoie
`drwx------. 2 nlefevre redaction`. Ce compte n'a jamais été créé localement, et
pourtant il se connecte, avec son groupe et son répertoire personnel.

> Le guide décrit un « piège du TLS » : SSSD refuserait d'envoyer un mot de passe
> sur une liaison `ldap://` non chiffrée, d'où la directive
> `ldap_auth_disable_tls_never_use_in_production`. Mesuré sur SSSD 2.12
> (AlmaLinux 10), l'authentification **réussit sans cette directive**, et
> `sssctl config-check` la rejette comme non autorisée. Le conseil de fond reste
> entier : en production on chiffre la liaison (`ldaps://` ou
> `ldap_id_use_start_tls = True` avec un certificat de confiance).

### Le cache de SSSD : la panne « j'ai corrigé et ça ne change rien »

SSSD met en cache les identités **et les absences d'identité**, sur disque, dans
`/var/lib/sss/db/`. C'est la première cause de faux diagnostic. Après avoir
changé le shell de l'utilisateur dans l'annuaire :

```bash
ldapsearch -x -H ldap://127.0.0.1 -b "dc=atelier,dc=demo" "(uid=nlefevre)" loginShell
getent passwd nlefevre
```

```text
loginShell: /bin/zsh
nlefevre:*:4201:4200:Nadia Lefevre:/home/nlefevre:/bin/bash
```

Et surtout, **redémarrer le service ne suffit pas**, puisque le cache survit au
redémarrage :

```bash
sudo systemctl restart sssd && getent passwd nlefevre   # toujours /bin/bash
sudo sss_cache -E        && getent passwd nlefevre      # /bin/zsh
```

Le cache négatif est encore plus déroutant : un compte interrogé **avant** son
existence reste introuvable quelques secondes après sa création.

```bash
getent passwd tmartin      # rc=2, le compte n'existe pas encore
# ... création de l'entrée dans l'annuaire ...
getent passwd tmartin      # rc=2 : c'est le cache négatif qui répond
sudo sss_cache -E
getent passwd tmartin
```

```text
tmartin:*:4202:4200:Theo Martin:/home/tmartin:/bin/bash
```

Réflexe à prendre : `sudo sss_cache -E` après **chaque** modification côté
annuaire, avant de conclure quoi que ce soit.

### Dépanner

`sssctl` (paquet `sssd-tools`) donne les deux réponses les plus utiles : la
configuration est-elle valide, et le domaine est-il joignable ?

```bash
sudo sssctl config-check
sudo sssctl domain-status ATELIER
```

```text
Issues identified by validators: 0

Online status: Online

Active servers:
LDAP: 10.10.30.14
```

Pour illustrer l'indépendance NSS/PAM annoncée en tête de cours : en retirant
`pam` de la ligne `services =` de `sssd.conf`, `getent passwd nlefevre` continue
de répondre, mais `su - nlefevre` échoue sur `su: Authentication failure`, et le
journal donne la vraie raison : `pam_sss(su-l:auth): Request to sssd failed.
Connection refused`. Le répondeur PAM de SSSD n'était tout simplement pas lancé.

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `getent passwd` ne renvoie rien alors que `sssd` tourne | `sss` absent de `nsswitch.conf` | `authselect current`, `grep ^passwd: /etc/nsswitch.conf` |
| `sssd` ne démarre pas | `sssd.conf` lisible par d'autres | `journalctl -u sssd`, puis `chmod 0600` |
| Résolution OK, connexion refusée | `pam` absent de `services =`, ou PAM non basculé | `pam_sss` dans `/etc/pam.d/system-auth` |
| Une correction reste sans effet | cache SSSD | `sss_cache -E` (un `restart` ne suffit pas) |
| Connexion OK mais pas de home | `oddjobd` à l'arrêt | `systemctl is-active oddjobd` |
| Pas de shell (`/usr/sbin/nologin`) | l'annuaire ne fournit pas `loginShell` | `default_shell` dans `sssd.conf` |
| L'utilisateur résout, pas son groupe | le groupe n'est pas lisible par le bind utilisé | comparer `ldapsearch -x` anonyme et authentifié |

La dernière ligne mérite un mot, car elle est arrivée sur cette machine :
`getent passwd` répondait, `getent group` non, et SSSD n'y était pour rien. Le
serveur 389 n'autorisait la lecture anonyme des groupes que pour les entrées
`groupOfNames`, alors que le groupe créé n'était qu'un `posixGroup`. Un
`ldapsearch -x` anonyme ne renvoyait rien, le même `ldapsearch` authentifié
renvoyait bien l'entrée. Quand les deux ne donnent pas le même résultat, le
problème est dans les droits de l'annuaire, pas dans le client. En production on
ne s'appuie d'ailleurs pas sur le bind anonyme : on déclare un compte de service
en lecture seule (`ldap_default_bind_dn` et `ldap_default_authtok`), et on
restreint qui peut se connecter avec `access_provider = ldap` et un filtre.
