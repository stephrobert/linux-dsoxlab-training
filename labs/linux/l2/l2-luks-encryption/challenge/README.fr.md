# Protéger les données au repos avec LUKS

## La situation

Sur **alma-rhcsa-1.lab**, un disque amovible va contenir des exports sensibles.
Si le disque quitte les locaux, son contenu doit rester illisible. Vous le
chiffrez avec **LUKS2** et le faites déverrouiller automatiquement au démarrage
via un fichier-clé.

Le disque libre à traiter est désigné dans `/root/luks-disk.env`, et la clé qui
servira à l'ouvrir est déjà déposée sur la machine.

Méthode dans le guide associé :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/

## L2 : Chiffrer un disque avec LUKS

### Mission

Un disque libre est disponible sur **alma-rhcsa-1.lab** (son nom est dans
`/root/luks-disk.env`), avec un fichier de clé `/root/luks.key`. Chiffre-le pour
que ses données soient illisibles en cas de vol du disque.

1. Formate le disque en **LUKS2** (utilise le fichier de clé).
2. **Ouvre**-le sous `/dev/mapper/coffre`.
3. Pose un système de fichiers **xfs** dessus et monte-le sur `/mnt/coffre`.
4. Déclare-le dans **`/etc/crypttab`** pour qu'il se déverrouille au démarrage.

### Contraintes

- Le disque doit être en **LUKS version 2**.
- `/dev/mapper/coffre` doit être ouvert et monté sur `/mnt/coffre`.
- `/etc/crypttab` doit contenir l'entrée `coffre`.

### Approche utile

Les gestes se déduisent du guide compagnon, dont le lien figure dans le
`## Rappel` du cours. Si tu bloques, `dsoxlab hint` les donne, au prix
annoncé.

### Validation

```bash
dsoxlab check l2-luks-encryption
```
