# Challenge — l2-fstab-persist-uuid

## Mission

Un disque additionnel est déjà formaté en **ext4** sur la VM, mais ni monté ni
déclaré. Monte-le sur `/srv/data` de façon **persistante**.

## Objectif (état attendu)

1. `/srv/data` est un point de montage **actif**.
2. Le filesystem monté est **ext4**.
3. `/etc/fstab` a une entrée pour `/srv/data` référencée **par UUID** (pas `/dev/vdX`).
4. L'UUID de fstab correspond au disque réellement monté (`mount -a` passe).

## Contraintes

- Récupère l'UUID avec `blkid` ou `lsblk -f`. N'écris pas le nom de périphérique.
- La validation interroge l'**état réel** de la VM (montage, type, contenu fstab).

## Validation

```bash
dsoxlab check l2-fstab-persist-uuid
```
