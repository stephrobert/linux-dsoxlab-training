# Lab — Chiffrer un disque avec LUKS

## Rappel

[**Le chiffrement de disque avec LUKS**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/)

LUKS chiffre un périphérique bloc : sans la clé, les données sont illisibles.
L'ordre est toujours format -> open -> mkfs sur le mapping -> mount. La
persistance se déclare dans `/etc/crypttab` (qui crée `/dev/mapper/...`) plus
`/etc/fstab`.

## Le cours

Les exemples ci-dessous travaillent sur un conteneur de démonstration
`/srv/archives.img` de 256 Mio, ouvert sous le nom `voute` et monté sur
`/mnt/archives` : le challenge, lui, vous donnera un autre périphérique, un
autre nom de mapping, un autre point de montage et un autre système de
fichiers. Le but est d'apprendre la méthode, pas de recopier une ligne.

> **`cryptsetup luksFormat` détruit le contenu du périphérique visé, sans
> retour arrière.** Avant chaque commande de ce cours, identifiez la cible avec
> `lsblk` et `losetup -a`, et n'agissez que sur un périphérique que vous avez
> créé vous-même. Se tromper de disque, c'est perdre son contenu.

### Où en est la machine

L'outil s'appelle `cryptsetup`. Sur une image AlmaLinux minimale il n'est pas
installé :

```bash
cryptsetup --version          # « command not found » avant installation
sudo dnf -y install cryptsetup
```

Une fois présent, il annonce sa version et les fonctions compilées :

```text
cryptsetup 2.8.1 flags: UDEV BLKID KEYRING FIPS KERNEL_CAPI PWQUALITY HW_OPAL
```

Retenez le drapeau **`PWQUALITY`** : cette version refuse les passphrases jugées
trop faibles, on le vérifiera plus bas.

Regardez ensuite quels périphériques existent, et lesquels sont libres :

```bash
lsblk
sudo losetup -a
```

### Le support de démonstration : un fichier conteneur

Pas besoin d'un disque libre pour apprendre : LUKS chiffre aussi bien un
**fichier**, présenté au noyau comme un périphérique bloc par `losetup`.

```bash
sudo dd if=/dev/zero of=/srv/archives.img bs=1M count=256 status=none
sudo losetup --find --show /srv/archives.img
```

```text
/dev/loop1
```

`--find` prend le premier numéro de boucle libre, `--show` l'affiche. **Notez
ce nom, c'est votre cible pour toute la suite.** Vérifiez immédiatement qu'il
pointe bien sur votre fichier, et sur rien d'autre :

```bash
sudo losetup -a
lsblk
```

```text
/dev/loop1: [64516]:8590690 (/srv/archives.img)
```

```text
NAME    MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINTS
loop1     7:1    0  256M  0 loop
```

### Chiffrer le volume : `luksFormat`

L'ordre est immuable : **formater, ouvrir, créer le système de fichiers sur le
mapping, monter**. Le système de fichiers se met **toujours** sur
`/dev/mapper/...`, jamais sur le périphérique chiffré brut.

```bash
sudo cryptsetup luksFormat --type luks2 /dev/loop1
```

La commande prévient, exige une confirmation en majuscules, puis demande la
passphrase deux fois :

```text
WARNING!
========
This will overwrite data on /dev/loop1 irrevocably.

Are you sure? (Type 'yes' in capital letters): Enter passphrase for /srv/archives.img:
Verify passphrase:
```

Deux détails à lire dans cette sortie. Le mot attendu est bien **`YES`** en
capitales, un `yes` minuscule ne passe pas. Et la deuxième invite nomme
`/srv/archives.img`, pas `/dev/loop1` : `cryptsetup` remonte jusqu'au fichier
qui porte la boucle, ce qui est une confirmation gratuite que vous visez le bon
support.

La passphrase, elle, est filtrée. Avec cinq caractères :

```text
Password quality check failed:
 The password is shorter than 8 characters
```

C'est le drapeau `PWQUALITY` vu plus haut : `cryptsetup` délègue à
`libpwquality` et refuse en dessous de 8 caractères. Le format ne se fait pas,
le code de retour est `2`.

Le périphérique porte ensuite une signature LUKS :

```bash
sudo blkid /dev/loop1
```

```text
/dev/loop1: UUID="ce57a15e-cd9b-463b-975c-3a1c9b7b2736" TYPE="crypto_LUKS"
```

### Lire l'en-tête : `luksDump`

C'est la commande qui prouve ce que vous avez créé, plutôt que de le supposer.

```bash
sudo cryptsetup luksDump /dev/loop1
```

```text
LUKS header information
Version:       	2
Epoch:         	3
Metadata area: 	16384 [bytes]
Keyslots area: 	16744448 [bytes]
UUID:          	ce57a15e-cd9b-463b-975c-3a1c9b7b2736
Label:         	(no label)

Data segments:
  0: crypt
	offset: 16777216 [bytes]
	length: (whole device)
	cipher: aes-xts-plain64
	sector: 512 [bytes]

Keyslots:
  0: luks2
	Key:        512 bits
	Cipher:     aes-xts-plain64
	Cipher key: 512 bits
	PBKDF:      argon2id
	Time cost:  54
	Memory:     136594
	Threads:    2
	AF stripes: 4000
	AF hash:    sha256
```

(extrait : les sels et les empreintes ont été retirés.)

Ce que cette sortie établit, sans qu'on ait demandé rien de particulier :

- **`Version: 2`** : c'est bien du LUKS2. Le guide rappelle qu'il est le format
  par défaut depuis `cryptsetup` 2.1, avec un en-tête stocké en double et
  jusqu'à 32 emplacements de clé, contre 8 pour LUKS1.
- **`aes-xts-plain64`** avec une **clé de 512 bits** : XTS utilise deux clés, il
  s'agit donc d'AES-256 et non d'un hypothétique AES-512.
- **`argon2id`** pour la dérivation de clé, conçue pour résister au cassage par
  GPU, là où LUKS1 se limitait à PBKDF2. Les lignes `Time cost`, `Memory` et
  `Threads` sont calibrées à la création en fonction de la machine : c'est ce
  qui rend l'ouverture volontairement lente.
- **`offset: 16777216 [bytes]`** : les données commencent à **16 Mio** du début.
  Tout ce qui précède est l'en-tête, et sa taille explique la suite.

### Ouvrir, formater, monter

```bash
sudo cryptsetup open /dev/loop1 voute
```

```text
Enter passphrase for /srv/archives.img:
```

Le mapping déchiffré apparaît sous `/dev/mapper/` :

```bash
lsblk
ls -l /dev/mapper/
```

```text
NAME    MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINTS
loop1     7:1    0  256M  0 loop
└─voute 253:0    0  240M  0 crypt
```

```text
lrwxrwxrwx. 1 root root 7 Jul 22 12:39 voute -> ../dm-0
```

Le conteneur fait 256 Mio, le mapping n'en fait que **240** : les 16 Mio
manquants sont exactement l'en-tête repéré dans `luksDump`. C'est un coût fixe,
négligeable sur un vrai disque, très visible sur un petit conteneur.

`cryptsetup status` donne la vue complète du mapping ouvert :

```bash
sudo cryptsetup status voute
```

```text
/dev/mapper/voute is active.
  type:    LUKS2
  cipher:  aes-xts-plain64
  keysize: 512 [bits]
  key location: keyring
  device:  /dev/loop1
  loop:    /srv/archives.img
  sector size:  512 [bytes]
  offset:  32768 [512-byte units] (16777216 [bytes])
  size:    491520 [512-byte units] (251658240 [bytes])
  mode:    read/write
```

Reste à poser un système de fichiers **sur le mapping**, puis à le monter :

```bash
sudo mkfs.ext4 /dev/mapper/voute
sudo mkdir -p /mnt/archives
sudo mount /dev/mapper/voute /mnt/archives
findmnt -n /mnt/archives
```

```text
/mnt/archives /dev/mapper/voute ext4 rw,relatime,seclabel
```

Deux couches empilées, que `lsblk -f` montre bien :

```bash
lsblk -f /dev/loop1
```

```text
NAME    FSTYPE      FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
loop1   crypto_LUKS 2           ce57a15e-cd9b-463b-975c-3a1c9b7b2736
└─voute ext4        1.0         ba884bb7-2159-4d7e-b126-ea2f11fc3318  202.9M     0% /mnt/archives
```

**Deux UUID différents, et la distinction est capitale pour la suite** : celui
du conteneur chiffré (`crypto_LUKS`) sert à `/etc/crypttab`, celui du système de
fichiers sert à `/etc/fstab` quand on monte par UUID. Les confondre est l'erreur
classique.

### Vérifier que le chiffrement protège vraiment

Rien n'oblige à croire sur parole. Écrivons un marqueur dans le volume, puis
cherchons-le dans le conteneur brut :

```bash
echo "SECRET-DE-DEMONSTRATION-42" | sudo tee /mnt/archives/dossier.txt
sudo sync
sudo grep -c "SECRET-DE-DEMONSTRATION" /srv/archives.img
```

```text
0
```

Zéro occurrence, alors que le volume est **encore monté** et que le fichier est
parfaitement lisible par `cat`. Pour être sûr que la méthode de recherche n'est
pas en cause, le même essai sur un conteneur non chiffré rend bien une
correspondance :

```bash
sudo dd if=/dev/zero of=/srv/temoin.img bs=1M count=32 status=none
sudo mkfs.ext4 -q /srv/temoin.img
sudo mkdir -p /mnt/temoin && sudo mount -o loop /srv/temoin.img /mnt/temoin
echo "SECRET-DE-DEMONSTRATION-42" | sudo tee /mnt/temoin/dossier.txt >/dev/null
sudo sync && sudo umount /mnt/temoin
sudo grep -c "SECRET-DE-DEMONSTRATION" /srv/temoin.img
```

```text
1
```

Le témoin en clair rend le motif, le conteneur chiffré non. Fermons maintenant
le volume :

```bash
sudo umount /mnt/archives
sudo cryptsetup close voute
lsblk -f /dev/loop1
```

```text
NAME  FSTYPE      FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
loop1 crypto_LUKS 2           ce57a15e-cd9b-463b-975c-3a1c9b7b2736
```

Le système de fichiers a disparu de l'affichage, ainsi que son UUID. Il est
toujours là, mais illisible : sans la clé, le noyau ne voit qu'un
`crypto_LUKS`.

L'ordre du démontage n'est pas négociable. Tenter de fermer un volume encore
monté échoue proprement :

```bash
sudo cryptsetup close voute
```

```text
Device voute is still in use.
```

### Ajouter un fichier-clé et gérer les slots

LUKS2 garde plusieurs clés indépendantes dans des *key slots* : de quoi donner
un accès personnel à plusieurs administrateurs, puis en révoquer un sans toucher
aux autres. Pour un déverrouillage sans saisie, on enrôle un **fichier-clé**
plutôt qu'une passphrase :

```bash
sudo dd if=/dev/urandom of=/root/archives.key bs=512 count=4
sudo chmod 0400 /root/archives.key
sudo cryptsetup luksAddKey /dev/loop1 /root/archives.key
```

```text
Enter any existing passphrase:
```

L'invite dit l'essentiel : pour **ajouter** une clé, il faut déjà en connaître
une valide. LUKS ne permet pas d'enrôler une clé sur un volume auquel on n'a pas
déjà accès.

Le `chmod 0400` n'est pas décoratif : ce fichier ouvre le volume aussi bien que
la passphrase. Lisible par tous, il annule tout le bénéfice du chiffrement.

Les slots occupés se lisent dans `luksDump` :

```bash
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
```

```text
  0: luks2
  1: luks2
```

Le volume s'ouvre désormais sans aucune saisie :

```bash
sudo cryptsetup open /dev/loop1 voute --key-file /root/archives.key
```

Les autres opérations suivent la même logique :

```bash
sudo cryptsetup luksAddKey    /dev/loop1        # ajouter une passphrase
sudo cryptsetup luksChangeKey /dev/loop1        # remplacer une passphrase
sudo cryptsetup luksRemoveKey /dev/loop1        # supprimer la passphrase saisie
sudo cryptsetup luksKillSlot  /dev/loop1 2      # supprimer le slot numéro 2
```

`luksKillSlot` exige lui aussi une clé valide **autre** que celle du slot visé,
d'où le `--key-file` ci-dessous :

```bash
sudo cryptsetup luksKillSlot /dev/loop1 2 --key-file /root/archives.key
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
```

```text
  0: luks2
  1: luks2
```

### Sauvegarder l'en-tête, et pourquoi c'est vital

L'en-tête contient les clés chiffrées. **S'il est perdu ou corrompu, les données
sont perdues**, même avec la bonne passphrase. Une écriture accidentelle sur le
début du périphérique suffit, et c'est très exactement ce qui arrive quand on
lance un `mkfs` sur le périphérique chiffré brut au lieu du mapping.

```bash
sudo mkdir -p /root/secours
sudo cryptsetup luksHeaderBackup /dev/loop1 --header-backup-file /root/secours/archives-header.img
sudo ls -l --block-size=M /root/secours/archives-header.img
```

```text
-r--------. 1 root root 16M Jul 22 12:44 /root/secours/archives-header.img
```

Seize mégaoctets, la taille de l'en-tête relevée dans `luksDump`. Notez que
`cryptsetup` crée lui-même le fichier en `0400` : il sait que ce fichier est
sensible.

À quel point ? Vérifions l'avertissement du guide, qui dit qu'une sauvegarde
d'en-tête reste exploitable avec une passphrase **valide au moment de la
sauvegarde**, même supprimée depuis. Retirons la passphrase du slot 0 :

```bash
sudo cryptsetup luksRemoveKey /dev/loop1
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
sudo cryptsetup open --test-passphrase /dev/loop1
```

```text
  1: luks2
```

```text
No key available with this passphrase.
```

Le slot 0 a bien disparu et la passphrase ne sert plus à rien. Restaurons
maintenant la sauvegarde faite avant la suppression :

```bash
sudo cryptsetup luksHeaderRestore /dev/loop1 --header-backup-file /root/secours/archives-header.img
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
sudo cryptsetup open --test-passphrase /dev/loop1 ; echo "rc=$?"
```

```text
  0: luks2
  1: luks2
```

```text
rc=0
```

La passphrase « révoquée » rouvre le volume. **Un `luksRemoveKey` ne protège
donc en rien contre une ancienne sauvegarde d'en-tête.** Traitez ces
sauvegardes comme les données elles-mêmes : chiffrées, hors-ligne, et détruites
quand elles ne sont plus à jour.

`--test-passphrase` mérite d'être retenu au passage : il vérifie une clé sans
créer le moindre mapping, c'est l'outil de diagnostic le plus sûr.

### Déverrouiller au démarrage : `crypttab` puis `fstab`

Deux fichiers, deux rôles distincts. **`/etc/crypttab` crée le mapping**,
**`/etc/fstab` monte ce mapping**. On ne met jamais le périphérique chiffré brut
dans `fstab`.

La ligne de `crypttab` a quatre champs : nom du mapping, périphérique, clé,
options.

```bash
sudo cryptsetup luksUUID /dev/loop1
```

```text
ce57a15e-cd9b-463b-975c-3a1c9b7b2736
```

```text title="/etc/crypttab"
voute UUID=ce57a15e-cd9b-463b-975c-3a1c9b7b2736 /root/archives.key luks
```

Le troisième champ est le chemin du fichier-clé. Le mot **`none`** à sa place
demande la passphrase interactivement au démarrage.

```text title="/etc/fstab"
/dev/mapper/voute /mnt/archives ext4 defaults,nofail 0 2
```

L'option **`nofail`** évite qu'un volume absent ou non déverrouillé ne bloque le
démarrage : sur un support amovible, elle est indispensable.

Il n'est pas nécessaire de redémarrer pour tester. `systemd` génère une unité
par ligne de `crypttab`, qu'on peut démarrer à la main :

```bash
sudo systemctl daemon-reload
sudo systemctl start systemd-cryptsetup@voute.service
sudo systemctl is-active systemd-cryptsetup@voute.service
ls -l /dev/mapper/voute
```

```text
active
lrwxrwxrwx. 1 root root 7 Jul 22 12:44 /dev/mapper/voute -> ../dm-0
```

Le mapping est créé sans qu'on ait tapé `cryptsetup open` : c'est bien la ligne
de `crypttab` qui agit. Le montage se teste ensuite en ne donnant que le point
de montage, ce qui force `mount` à lire `fstab` :

```bash
sudo mount /mnt/archives
findmnt -n /mnt/archives
```

```text
/mnt/archives /dev/mapper/voute ext4 rw,relatime,seclabel
```

L'unité générée est instructive, et se lit sans rien installer :

```bash
sudo systemctl cat systemd-cryptsetup@voute.service
```

```text
# /run/systemd/generator/systemd-cryptsetup@voute.service
# Automatically generated by systemd-cryptsetup-generator
...
SourcePath=/etc/crypttab
RequiresMountsFor=/root/archives.key
BindsTo=dev-disk-by\x2duuid-ce57a15e\x2dcd9b\x2d463b\x2d975c\x2d3a1c9b7b2736.device
```

Trois enseignements. L'unité vit dans `/run/`, elle est **régénérée à chaque
`daemon-reload`** : n'allez pas l'éditer, corrigez `crypttab`. Le
`RequiresMountsFor` sur le fichier-clé impose que celui-ci soit sur un système
de fichiers **déjà monté** au moment du déverrouillage, ce qui exclut de le
poser sur le volume qu'il doit ouvrir. Et le `BindsTo` montre que l'UUID de
`crypttab` est résolu via `/dev/disk/by-uuid/` : une faute de frappe dans cet
UUID donne une unité qui attendra un périphérique qui n'arrivera jamais.

Le guide ajoute un geste que ce lab ne permet pas de vérifier : après
modification, **régénérer l'initramfs** pour que le déverrouillage fonctionne
tôt au démarrage, avec `sudo dracut --force` sur RHEL et AlmaLinux, ou
`sudo update-initramfs -u` sur Debian et Ubuntu. C'est indispensable dès que le
volume doit être ouvert avant le montage de la racine.

### Ce que LUKS ne protège pas

LUKS protège **au repos**. Une fois le volume déverrouillé et monté, les
fichiers sont en clair pour tout processus autorisé, comme le montre le simple
`cat` plus haut sur un volume dont le contenu brut est pourtant illisible. LUKS
répond au vol du disque, pas à l'intrusion sur un système en marche.

Le chiffrement est aussi une affaire de granularité : LUKS chiffre **tout le
volume**, ce qui convient à un disque, une partition ou du swap. Pour chiffrer
un sous-dossier synchronisé vers un cloud, le guide oriente vers un outil par
fichier comme `gocryptfs`, et déconseille `eCryptfs`, déprécié.

Côté coût, l'accélération AES-NI rend le surcoût négligeable devant la vitesse
d'un disque. La mesure se fait en une commande, sans toucher au stockage :

```bash
cryptsetup benchmark
```

```text
argon2id     52 iterations, 127546 memory, 4 parallel threads (CPUs) for 256-bit key (requested 2000 ms time)
#     Algorithm |       Key |      Encryption |      Decryption
        aes-cbc        256b      1298.5 MiB/s      5603.4 MiB/s
        aes-xts        256b      8087.8 MiB/s      8237.9 MiB/s
        aes-xts        512b      7439.7 MiB/s      7696.7 MiB/s
    serpent-xts        512b       778.5 MiB/s       789.7 MiB/s
```

(extrait, sur la VM de ce lab.) `aes-xts` avec une clé de 512 bits, le mode
retenu par défaut, tient plusieurs gigaoctets par seconde là où `serpent-xts`
plafonne dix fois plus bas. Le défaut n'est pas seulement sûr, il est aussi le
plus rapide.

Dernier réglage à connaître : le **TRIM** est désactivé par défaut sur un volume
chiffré, et `cryptsetup status` ne montre effectivement aucun drapeau
`discards`. L'activer (`cryptsetup open --allow-discards`, ou l'option `discard`
dans `crypttab`) améliore les performances d'un SSD, mais révèle au niveau
physique quels blocs sont utilisés. Sur un système sensible, laissez-le
désactivé.

Le guide décrit enfin le **NBDE** (Clevis et Tang), qui déverrouille
automatiquement un volume tant que la machine joint un serveur Tang, sans jamais
transmettre la clé, ainsi que la variante liée au **TPM2**. Les paquets `clevis`
et `tang` ne sont pas présents sur cette VM : c'est une lecture, pas une
manipulation de ce lab.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `Password quality check failed: The password is shorter than 8 characters` | `cryptsetup` est compilé avec `PWQUALITY` : il faut au moins 8 caractères |
| `No key available with this passphrase` | mauvaise passphrase, ou slot supprimé : vérifier avec `luksDump` et `open --test-passphrase` |
| `Device voute already exists` | le mapping est déjà ouvert : `cryptsetup close voute` avant de rouvrir |
| `Device voute is still in use` | le volume est encore monté : `umount` d'abord, `close` ensuite |
| `luksAddKey` n'aboutit pas | il faut fournir une clé **déjà valide** pour en enrôler une nouvelle |
| Le mapping fait moins que le périphérique | normal : l'en-tête LUKS2 occupe les 16 premiers Mio |
| `mkfs` a détruit le volume | le système de fichiers a été posé sur le périphérique brut, pas sur `/dev/mapper/...` |
| Le volume n'est pas déverrouillé au démarrage | ligne `crypttab` absente ou fautive, ou initramfs non régénéré (`dracut --force`) |
| L'unité `systemd-cryptsetup@…` reste en attente | l'UUID de `crypttab` ne correspond à aucun périphérique : comparer avec `cryptsetup luksUUID` |
| Le fichier-clé n'est pas trouvé au démarrage | il est sur un système de fichiers pas encore monté à ce stade |
| Données illisibles après un incident sur l'en-tête | restaurer avec `cryptsetup luksHeaderRestore` |
| L'ouverture est lente | `argon2id` consomme volontairement RAM et CPU, c'est la protection anti-force brute |

Pour tout défaire et repartir de zéro :

```bash
sudo umount /mnt/archives
sudo systemctl stop systemd-cryptsetup@voute.service   # ou : sudo cryptsetup close voute
sudo sed -i '/^voute /d' /etc/crypttab
sudo sed -i '\|^/dev/mapper/voute |d' /etc/fstab
sudo systemctl daemon-reload
sudo losetup -d /dev/loop1
sudo rm -f /srv/archives.img /root/archives.key /root/secours/archives-header.img
sudo rmdir /root/secours /mnt/archives
```

Le `losetup -d` n'est pas un détail : sans lui, la boucle reste attachée à un
fichier supprimé et occupe un numéro de périphérique jusqu'au redémarrage.
Contrôlez le retour au point de départ avec `lsblk`, `sudo losetup -a` et
`sudo dmsetup ls`.
