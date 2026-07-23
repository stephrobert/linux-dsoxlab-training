# Challenge — l2 : Chiffrer un disque avec LUKS

## Mission

Un disque libre est disponible sur **alma-rhcsa-1.lab** (son nom est dans
`/root/luks-disk.env`), avec un fichier de clé `/root/luks.key`. Chiffre-le pour
que ses données soient illisibles en cas de vol du disque.

1. Formate le disque en **LUKS2** (utilise le fichier de clé).
2. **Ouvre**-le sous `/dev/mapper/coffre`.
3. Pose un système de fichiers **xfs** dessus et monte-le sur `/mnt/coffre`.
4. Déclare-le dans **`/etc/crypttab`** pour qu'il se déverrouille au démarrage.

## Contraintes

- Le disque doit être en **LUKS version 2**.
- `/dev/mapper/coffre` doit être ouvert et monté sur `/mnt/coffre`.
- `/etc/crypttab` doit contenir l'entrée `coffre`.

## Approche utile

Les gestes se déduisent du guide compagnon, dont le lien figure dans le
`## Rappel` du cours. Si tu bloques, `dsoxlab hint` les donne, au prix
annoncé.

## Validation

```bash
dsoxlab check l2-luks-encryption
```
