# Challenge — l2-fstab-persist-uuid

## Mission

Un disque additionnel est déjà formaté en **ext4** sur la VM, mais ni monté ni
déclaré. Monte-le sur `/srv/data` de façon **persistante**.

## Objectif (état attendu)

1. `/srv/data` est un point de montage **actif**.
2. Le filesystem monté est **ext4**.
3. `/etc/fstab` a une entrée pour `/srv/data` référencée **par UUID** (pas
   `/dev/vdX`), dont le champ **type** est `ext4` (ou `auto`).
4. L'UUID de fstab correspond au disque réellement monté.
5. `sudo findmnt --verify` ne signale **ni `parse error` ni `error`** sur ta
   ligne : c'est elle qui prouve que le montage se refera au démarrage.

## Contraintes

- Récupère l'UUID avec `blkid` ou `lsblk -f`. N'écris pas le nom de périphérique.
- `sudo mount -a` **ne suffit pas** à valider un `fstab` : il sort en 0 sur une
  ligne fautive qui est déjà montée, ou dont la source est introuvable mais
  couverte par `nofail`. Contrôle toujours avec les deux commandes :
  `sudo systemctl daemon-reload`, puis `sudo findmnt --verify`, puis
  `sudo mount -a`.
- La validation interroge l'**état réel** de la VM (montage, type, contenu
  fstab, verdict de `findmnt --verify`).

## Validation

```bash
dsoxlab check l2-fstab-persist-uuid
```
