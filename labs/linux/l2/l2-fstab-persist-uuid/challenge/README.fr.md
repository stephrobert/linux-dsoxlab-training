# Rendre un montage résistant au reboot

## La situation

La machine a un disque supplémentaire, déjà formaté en ext4, mais il n'est ni
monté ni déclaré. Ta mission : le monter sur `/srv/data` et rendre ce montage
**permanent** : le genre de tâche qui fait échouer les candidats RHCSA quand ils
montent à la main sans rien déclarer, ou quand ils référencent le disque par un
nom de périphérique qui peut changer au prochain démarrage.

L'idée : les noms de périphériques (`/dev/vdb`) ne sont pas stables d'un reboot à
l'autre ; un UUID l'est. Reste à savoir où se déclare un montage permanent, et
comment y désigner le disque autrement que par son nom de périphérique.

Reste surtout une question que beaucoup escamotent : une fois la ligne écrite,
comment savoir qu'elle est bonne **avant** de redémarrer ? Un serveur qui ne
remonte pas se découvre au pire moment, et l'outil que tout le monde cite ne
voit pas tout.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/

## Ce qui est demandé

### Mission

Un disque additionnel est déjà formaté en **ext4** sur la VM, mais ni monté ni
déclaré. Monte-le sur `/srv/data` de façon **persistante**.

### Objectif (état attendu)

1. `/srv/data` est un point de montage **actif**.
2. Le filesystem monté est **ext4**.
3. `/etc/fstab` a une entrée pour `/srv/data` référencée **par UUID** (pas
   `/dev/vdX`), dont le champ **type** est `ext4` (ou `auto`).
4. L'UUID de fstab correspond au disque réellement monté.
5. `sudo findmnt --verify` ne signale **ni `parse error` ni `error`** sur ta
   ligne : c'est elle qui prouve que le montage se refera au démarrage.

### Contraintes

- Récupère l'UUID avec `blkid` ou `lsblk -f`. N'écris pas le nom de périphérique.
- `sudo mount -a` **ne suffit pas** à valider un `fstab` : il sort en 0 sur une
  ligne fautive qui est déjà montée, ou dont la source est introuvable mais
  couverte par `nofail`. Contrôle toujours avec les deux commandes :
  `sudo systemctl daemon-reload`, puis `sudo findmnt --verify`, puis
  `sudo mount -a`.
- La validation interroge l'**état réel** de la VM (montage, type, contenu
  fstab, verdict de `findmnt --verify`).

### Validation

```bash
dsoxlab check l2-fstab-persist-uuid
```
