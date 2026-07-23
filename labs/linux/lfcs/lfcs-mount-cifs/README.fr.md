# Lab — montage SMB/CIFS persistant

## Rappel

[**SMB sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/stockage/smb/)

Un montage CIFS demande le paquet `cifs-utils` et un partage authentifié :
`mount -t cifs //<serveur>/<partage> <point-de-montage> -o credentials=<fichier>`.

Deux choses le rendent digne de la production :

- **`_netdev`** dans `/etc/fstab` : le montage est classé comme montage réseau ;
- un **fichier credentials** (lignes `username=` / `password=`) en `0600`, parce
  que `/etc/fstab` est lisible par tous et ne doit jamais contenir de mot de
  passe.

## Le cours

Les exemples ci-dessous montent un partage `documents` sur `/mnt/documents`, avec
un compte SMB `archiviste` : le challenge, lui, portera sur un autre partage, un
autre point de montage et un autre compte. Apprenez l'enchaînement, ne recopiez
pas une ligne. Toutes les sorties viennent d'une VM **Ubuntu 24.04.4** (noyau
**6.8.0-134-generic**), avec **Samba 4.19.5** et **cifs-utils 2:7.0**, la même
image que celle du lab.

### Le décor : serveur et client sur la même machine

Pour apprendre, une seule machine suffit : on y monte un petit serveur Samba et
on s'y connecte par `127.0.0.1`. Le paquet `samba` fournit le serveur,
`cifs-utils` le client (il apporte l'assistant `/sbin/mount.cifs`, sans lequel
`mount -t cifs` échoue sur un message trompeur, mesuré ici : `cannot mount
//127.0.0.1/documents read-only.`), et `smbclient` l'outil d'exploration.

```bash
sudo apt-get install -y samba cifs-utils smbclient
sudo mkdir -p /srv/documents-demo/rapports
echo "inventaire des documents de l atelier" | sudo tee /srv/documents-demo/note.txt
sudo useradd --system --no-create-home --shell /usr/sbin/nologin archiviste
sudo chown -R archiviste:archiviste /srv/documents-demo   # uid 999, gid 987
```

```ini title="/etc/samba/smb.conf"
[global]
   workgroup = ATELIER
   security = user
   server min protocol = SMB3
   restrict anonymous = 2
[documents]
   path = /srv/documents-demo
   read only = no
   valid users = archiviste
```

Un compte SMB n'est pas un compte Unix : le mot de passe vit dans la base Samba,
posé par `smbpasswd`, pas dans `/etc/shadow`.

```bash
(echo "Demo-Cifs-2026"; echo "Demo-Cifs-2026") | sudo smbpasswd -a -s archiviste
sudo systemctl restart smbd && ss -tlnp | grep :445
```

```text
Added user archiviste.
LISTEN 0      50           0.0.0.0:445       0.0.0.0:*
```

> **Un montage sur soi-même passe-t-il par le réseau ?** Oui : partage monté,
> `ss -tn state established '( sport = :445 or dport = :445 )'` montre une vraie
> connexion TCP, `127.0.0.1:445` face à `127.0.0.1:51892`. Tout ce qui suit vaut
> donc pour un serveur distant. Une seule limite : sur une même machine le réseau
> est toujours prêt au démarrage, ce décor ne peut pas prouver l'utilité de
> `_netdev`. Nous la lirons dans les dépendances systemd.

### Voir le partage, puis le monter à la main

`smbclient -L` liste les partages d'un serveur. C'est la première commande à
lancer quand un montage échoue : si elle ne répond pas, le problème est côté
serveur ou réseau, inutile de chercher dans `fstab`.

```bash
smbclient -L //127.0.0.1 -U archiviste
```

```text
	Sharename       Type      Comment
	---------       ----      -------
	documents       Disk
	IPC$            IPC       IPC Service (Samba 4.19.5-Ubuntu)
```

Montons maintenant. Retenez la forme du premier argument :
**`//serveur/partage`**, avec deux barres obliques et **pas** de chemin système
(CIFS ne connaît que le nom du partage, contrairement à NFS où l'on écrit
`serveur:/chemin/exporté`).

```bash
sudo mkdir -p /mnt/documents
sudo mount -t cifs //127.0.0.1/documents /mnt/documents \
  -o username=archiviste,password=Demo-Cifs-2026
findmnt /mnt/documents
```

```text
TARGET         SOURCE                FSTYPE OPTIONS
/mnt/documents //127.0.0.1/documents cifs   rw,relatime,vers=3.1.1,[...],username=archiviste,
uid=0,noforceuid,gid=0,noforcegid,addr=127.0.0.1,file_mode=0755,dir_mode=0755,soft,nounix,[...]
```

Cette ligne d'options contient trois réponses : la version négociée
(`vers=3.1.1`), l'identité imposée aux fichiers (`uid=0`, `gid=0`) et les droits
affichés (`file_mode=0755`). Nous y revenons plus bas.

### Le mot de passe n'a rien à faire dans `/etc/fstab`

C'est le point de sécurité du sujet, et il tient dans une commande :
`stat -c "%a %U:%G" /etc/fstab` répond **`644 root:root`**.

`/etc/fstab` est lisible par **tout le monde**, et il doit l'être : `mount`,
`findmnt` et les outils système le consultent sans privilège. Une ligne écrite
avec `password=` y expose donc le mot de passe du compte SMB à chaque utilisateur
de la machine. Vérifié depuis un compte ordinaire :

```bash
sudo -u stagiaire grep -o 'password=[^,]*' /etc/fstab
```

```text
password=Demo-Cifs-2026 0 0
```

La bonne pratique, et ce que l'examen attend : un **fichier credentials** dont le
format est donné par `man mount.cifs` (`username=`, `password=`, et
optionnellement `domain=`), protégé en `0600`.

```bash
printf 'username=archiviste\npassword=Demo-Cifs-2026\ndomain=ATELIER\n' \
  | sudo tee /etc/atelier-smb.cred > /dev/null
sudo chmod 0600 /etc/atelier-smb.cred && ls -l /etc/atelier-smb.cred
sudo -u stagiaire cat /etc/atelier-smb.cred
```

```text
-rw------- 1 root root 59 Jul 22 18:30 /etc/atelier-smb.cred
cat: /etc/atelier-smb.cred: Permission denied
```

`/etc/fstab` ne porte plus alors que `credentials=/etc/atelier-smb.cred` : le
chemin est public, le contenu ne l'est pas. Deux pièges de rédaction :
**pas de guillemets** autour de la valeur (`password="Demo-Cifs-2026"` fait
échouer le montage avec `mount error(13): Permission denied`, les guillemets
étant pris pour des caractères du mot de passe), et **pas d'espace** autour du
signe `=`.

### Qui possède les fichiers ? `uid`, `gid`, `file_mode`, `dir_mode`

Voici ce qui déroute le plus, et ce qui sépare vraiment CIFS de NFS. Comparons le
même fichier vu du serveur et vu à travers le montage posé plus haut :

```bash
ls -ln /srv/documents-demo      # cote serveur
ls -ln /mnt/documents           # a travers le montage
```

```text
-rw-r--r-- 1 999 987   38 Jul 22 18:30 note.txt      <- serveur
-rwxr-xr-x 1   0   0   38 Jul 22 18:30 note.txt      <- client
```

Le propriétaire (999) est devenu `root`, et les droits `0644` sont devenus
`0755`. Rien n'a bougé sur le serveur : c'est l'affichage côté client qui est
**fabriqué de toutes pièces**. Conséquence immédiate, un utilisateur non
privilégié ne peut rien écrire : `touch: cannot touch
'/mnt/documents/essai-ansible.txt': Permission denied`.

**Pourquoi.** Le protocole SMB n'achemine pas les identités POSIX. Le client
ouvre une **session authentifiée** avec un compte SMB, et le serveur applique ses
propres droits à ce compte ; il n'a rien à dire sur l'UID que le client doit
afficher. Le client CIFS invente donc une identité locale, dont le défaut est
`uid=0` (`man mount.cifs` : « *sets the uid that will own all files [...] when
the server does not provide ownership information. [...] the default is uid 0* »).
NFS fait l'inverse : il transporte des UID et GID numériques, ce qui produit des
symptômes opposés (fichiers appartenant à `nobody` par `root_squash`). D'où des
options `uid=` / `gid=` / `file_mode=` / `dir_mode=` propres à CIFS, sans
équivalent NFS.

Remontons en choisissant l'identité affichée :

```bash
sudo umount /mnt/documents
sudo mount -t cifs //127.0.0.1/documents /mnt/documents \
  -o credentials=/etc/atelier-smb.cred,uid=ansible,gid=ansible
ls -l /mnt/documents ; touch /mnt/documents/essai-ansible.txt ; echo "rc=$?"
```

```text
-rwxr-xr-x 1 ansible ansible 38 Jul 22 18:30 note.txt
rc=0
```

L'écriture passe. Mais regardez le même fichier **côté serveur** :

```text
-rwxr--r-- 1 999 987 0 Jul 22 18:30 /srv/documents-demo/essai-ansible.txt
```

Il appartient à `archiviste`, le compte de la session SMB, pas à `ansible`.
Retenez la règle : **`uid=` ne change que la vue du client ; côté serveur, tout
est fait au nom du compte authentifié.** Ce n'est pas un contrôle d'accès, c'est
un habillage, et `findmnt` le dit, l'option passant de `uid=0,noforceuid` à
`uid=1001,forceuid`. `file_mode=` et `dir_mode=` habillent les droits de la même
manière :

```bash
sudo mount -t cifs //127.0.0.1/documents /mnt/documents \
  -o credentials=/etc/atelier-smb.cred,uid=ansible,gid=ansible,file_mode=0640,dir_mode=0750
ls -l /mnt/documents ; chmod 0600 /mnt/documents/note.txt ; echo "rc=$?"
ls -l /mnt/documents/note.txt
```

```text
-rw-r----- 1 ansible ansible 38 Jul 22 18:30 note.txt
drwxr-x--- 2 ansible ansible  0 Jul 22 18:30 rapports
rc=0
-rw-r----- 1 ansible ansible 38 Jul 22 18:30 note.txt      <- inchange
```

Le `chmod` **rend 0 et ne change rien** : sans les extensions Unix (le montage
est en `nounix`), le mode affiché reste celui de `file_mode`, sur le client comme
sur le serveur. Un échec silencieux qu'il faut connaître avant de perdre une
heure dessus.

### Rendre le montage persistant : `_netdev` et `nofail`

**Sauvegardez `/etc/fstab` avant de l'éditer** (`sudo cp -a /etc/fstab
/root/fstab.avant-cifs`) : une erreur ici se paie au démarrage suivant.

```text title="/etc/fstab"
//127.0.0.1/documents /mnt/documents cifs _netdev,nofail,credentials=/etc/atelier-smb.cred,uid=ansible,gid=ansible,file_mode=0640,dir_mode=0750 0 0
```

Six champs, comme pour un disque local : source `//serveur/partage`, point de
montage, type `cifs`, options, puis `0 0` (un partage réseau ne se sauvegarde ni
ne se vérifie localement). Puis, dans cet ordre :

```bash
sudo systemctl daemon-reload    # systemd relit fstab
sudo findmnt --verify           # controle syntaxique
sudo mount -a                   # applique sans redemarrer
findmnt -no SOURCE,TARGET,FSTYPE /mnt/documents
```

```text
Success, no errors or warnings detected
//127.0.0.1/documents /mnt/documents cifs
```

`mount -a` est rejouable : relancé alors que le partage est déjà monté, il ne
fait rien et rend 0.

> **Ne testez jamais une ligne `fstab` par un redémarrage.** `findmnt --verify`
> lit la syntaxe, `mount -a` prouve que la ligne monte réellement, et
> `systemctl show <unité>.mount` prouve le reste. Un redémarrage sur une ligne
> douteuse coûte une minute et demie d'attente par entrée injoignable, et rend
> une machine dégradée si l'entrée n'a pas `nofail`.

**Ce que `nofail` change**, lu par `systemctl show remote-fs.target -p Requires
-p Wants` avec puis sans l'option :

```text
avec nofail :  Requires=                       Wants=mnt-documents.mount
sans nofail :  Requires=mnt-documents.mount    Wants=
```

Le montage passe de `Requires` à `Wants` : son échec n'entraîne plus celui de la
cible, donc plus un démarrage dégradé. L'attente, elle, subsiste mais reste
bornée (`systemctl show mnt-documents.mount -p TimeoutUSec` répond
`TimeoutUSec=1min 30s`).

**Ce que `_netdev` change**, sur cette machine : rien de mesurable. Les mêmes
`systemctl show -p Wants -p After` avec et sans l'option renvoient exactement
`Wants=network-online.target` et le même ordonnancement après
`network-online.target` et `remote-fs-pre.target`. Comme pour `nfs`, systemd sait
déjà que `cifs` est un système de fichiers réseau et le classe seul. Écrivez
`_netdev` quand même : l'examen LFCS l'attend, elle documente l'intention, et
elle devient indispensable dès qu'un système de fichiers **local** repose sur un
transport réseau (un `ext4` sur volume iSCSI, que systemd ne peut pas deviner).

### La version du dialecte : ne forcez pas `vers=3.0`

Le guide compagnon conseille `-o vers=3.0` pour « forcer SMB3 » plutôt que de
laisser négocier. Sur cette machine, **le conseil est contre-productif** : avec
`credentials=/etc/atelier-smb.cred,vers=3.0`, le montage échoue, et `dmesg` dit
pourquoi.

```text
mount error(95): Operation not supported
CIFS: VFS: \\127.0.0.1 Dialect not supported by server.
```

Deux pages de manuel de la machine expliquent ce refus. `man mount.cifs` : « *If
no dialect is specified on mount `vers=default` is used* », qui négocie la
**version la plus haute commune**, ici **3.1.1**, donc meilleure que 3.0. Et
`man smb.conf` : la valeur `SMB3` de `server min protocol` est un alias de
`SMB3_11`, soit SMB 3.1.1 ; un serveur ainsi durci refuse donc SMB 3.0.0. Avec
`server min protocol = SMB3_00`, le même `vers=3.0` passe.

Conclusion : **laissez négocier**, et vérifiez le dialecte obtenu, soit dans les
options (`findmnt -no OPTIONS /mnt/documents` contient `vers=3.1.1`), soit dans
le fichier que `man mount.cifs` désigne pour cela :

```bash
sudo grep Dialect /proc/fs/cifs/DebugData      # Dialect 0x311 = SMB 3.1.1
```

Ne forcez une version que pour **descendre** vers un serveur ancien, jamais pour
monter : `vers=1.0` (SMB1, le vrai « CIFS » historique, celui d'EternalBlue) est
d'ailleurs refusé net par ce serveur, avec la même erreur 95.

### Dépannage et retour à l'état initial

Devant un `mount error(N)`, lisez `sudo dmesg | tail -3` : le code est vague, le
message noyau est précis.

| Symptôme | Cause probable | Solution |
|---|---|---|
| `cannot mount ... read-only.` | assistant `/sbin/mount.cifs` absent, donc paquet `cifs-utils` non installé | l'installer |
| `mount error(13): Permission denied`, dmesg `STATUS_LOGON_FAILURE` | mauvais identifiants, ou guillemets dans le fichier credentials | corriger le fichier, sans guillemets |
| `mount error(2)`, dmesg `BAD_NETWORK_NAME` | nom de partage inexistant | `smbclient -L //<serveur> -U <user>` |
| `error 2 opening credential file ...` | chemin `credentials=` erroné | vérifier le chemin, code de retour 2 |
| `mount error(95)`, dmesg `Dialect not supported` | `vers=` incompatible avec `server min protocol` | retirer `vers=`, laisser négocier |
| `mount error(113): could not connect` | serveur injoignable (6 s mesurées sur ce réseau) | route, adresse, pare-feu, port 445 |
| Tous les fichiers appartiennent à `root` | défaut `uid=0` du client CIFS | ajouter `uid=`/`gid=` |
| `chmod` rend 0 sans rien changer | montage `nounix` : les droits viennent de `file_mode` | ajuster `file_mode=`/`dir_mode=` |
| Le partage disparaît au redémarrage | pas de ligne dans `/etc/fstab` | l'ajouter, valider par `mount -a` |
| Un utilisateur lit le mot de passe SMB | `password=` dans `/etc/fstab` (mode 644) | fichier credentials en `0600` |

Pour tout défaire, dans cet ordre : démonter, restaurer `/etc/fstab` depuis la
copie prise **avant** l'édition, effacer les identifiants, arrêter le serveur.
N'oubliez pas le compte SMB : `smbpasswd -x` le retire de la base Samba, ce que
`userdel` ne fait pas.

```bash
sudo umount /mnt/documents
sudo cp -a /root/fstab.avant-cifs /etc/fstab && sudo systemctl daemon-reload
sudo shred -u /etc/atelier-smb.cred          # un mot de passe ne se rm pas
sudo systemctl disable --now smbd nmbd
sudo rm -rf /srv/documents-demo /mnt/documents
sudo smbpasswd -x archiviste && sudo userdel archiviste
findmnt -t cifs ; sudo pdbedit -L            # aucune sortie attendue
```
